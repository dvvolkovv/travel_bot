'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/lib/chat-store';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';

export function MessageStream({ nights }: { nights: number }) {
  const { messages, currentText, currentTrace, currentOffers, isStreaming } = useChatStore();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: 'smooth' });
  }, [messages, currentText, currentTrace, currentOffers]);

  return (
    <div ref={ref} className="flex-1 overflow-y-auto space-y-4 pr-2" aria-live="polite">
      {messages.map((m) =>
        m.role === 'user' ? (
          <UserMessage key={m.id} text={m.text} />
        ) : (
          <AssistantMessage key={m.id} text={m.text} offers={m.offers} trace={m.trace} nights={nights} />
        ),
      )}
      {isStreaming && (
        <AssistantMessage
          text={currentText}
          trace={currentTrace}
          offers={currentOffers ?? undefined}
          nights={nights}
          isStreaming
        />
      )}
    </div>
  );
}
