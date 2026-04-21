'use client';

import { useEffect, useRef } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useChatStore } from '@/lib/chat-store';
import { splitCards } from '@/lib/parse-cards';
import { streamTurn } from '@/lib/sse-client';
import { ChatInput } from '@/components/ChatInput';
import { MessageStream } from '@/components/MessageStream';
import { SuggestionChips } from '@/components/SuggestionChips';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

export default function ChatPage() {
  const { sessionId } = useParams() as { sessionId: string };
  const searchParams = useSearchParams();
  const initial = searchParams.get('q') ?? '';
  const t = useTranslations('chat');
  const store = useChatStore();
  const started = useRef(false);
  const nights = 5;

  const sendTurn = async (text: string) => {
    store.appendUserMessage(text);
    store.setStreaming(true);
    await streamTurn({
      url: '/api/chat/turn',
      body: { session_id: sessionId, message: text },
      onEvent: (type, data: any) => {
        if (type === 'thinking') store.appendTrace(data?.text ?? '...');
        else if (type === 'tool_call') store.appendTrace(t('searching'));
        else if (type === 'tool_result') store.appendTrace(data?.summary ?? t('filtering'));
        else if (type === 'token') {
          const next = (useChatStore.getState().currentText ?? '') + (data?.text ?? '');
          const { text: cleanText, offers } = splitCards(next);
          useChatStore.setState({ currentText: cleanText });
          if (offers) useChatStore.setState({ currentOffers: offers });
        } else if (type === 'cards') store.setOffers(data?.offers ?? []);
      },
      onDone: () => {
        store.commitAssistantMessage();
        store.setStreaming(false);
      },
      onError: () => {
        store.setStreaming(false);
      },
    });
  };

  useEffect(() => {
    store.setSessionId(sessionId);
    if (initial && !started.current) {
      started.current = true;
      void sendTurn(initial);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  return (
    <main className="flex flex-col h-screen max-w-3xl mx-auto px-4 py-4">
      <header className="flex justify-between items-center mb-4">
        <div className="font-semibold">Hotel Deals Bot</div>
        <LanguageSwitcher />
      </header>
      <MessageStream nights={nights} />
      <div className="pt-3">
        {!store.isStreaming && store.messages.length > 0 && (
          <SuggestionChips onPick={(txt) => void sendTurn(txt)} />
        )}
        <div className="mt-3">
          <ChatInput onSubmit={(txt) => void sendTurn(txt)} disabled={store.isStreaming} />
        </div>
      </div>
    </main>
  );
}
