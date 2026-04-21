import { create } from 'zustand';
import { nanoid } from 'nanoid';
import type { HotelOffer } from '@hotel-deals/shared-types';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  offers?: HotelOffer[];
  trace?: string[];
}

interface ChatStore {
  sessionId: string;
  messages: Message[];
  currentTrace: string[];
  currentText: string;
  currentOffers: HotelOffer[] | null;
  isStreaming: boolean;
  setSessionId: (id: string) => void;
  appendTrace: (line: string) => void;
  appendToken: (text: string) => void;
  setOffers: (offers: HotelOffer[]) => void;
  commitAssistantMessage: () => void;
  appendUserMessage: (text: string) => void;
  setStreaming: (on: boolean) => void;
  reset: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  sessionId: '',
  messages: [],
  currentTrace: [],
  currentText: '',
  currentOffers: null,
  isStreaming: false,
  setSessionId: (id) => set({ sessionId: id }),
  appendTrace: (line) => set((s) => ({ currentTrace: [...s.currentTrace, line] })),
  appendToken: (t) => set((s) => ({ currentText: s.currentText + t })),
  setOffers: (offers) => set({ currentOffers: offers }),
  commitAssistantMessage: () =>
    set((s) => {
      const hasContent = s.currentText.trim() || (s.currentOffers && s.currentOffers.length > 0);
      if (!hasContent) {
        return { currentTrace: [], currentText: '', currentOffers: null };
      }
      return {
        messages: [
          ...s.messages,
          {
            id: nanoid(),
            role: 'assistant',
            text: s.currentText,
            offers: s.currentOffers ?? undefined,
            trace: s.currentTrace,
          },
        ],
        currentTrace: [],
        currentText: '',
        currentOffers: null,
      };
    }),
  appendUserMessage: (text) =>
    set((s) => ({
      messages: [...s.messages, { id: nanoid(), role: 'user', text }],
    })),
  setStreaming: (on) => set({ isStreaming: on }),
  reset: () =>
    set({ messages: [], currentTrace: [], currentText: '', currentOffers: null, isStreaming: false }),
}));
