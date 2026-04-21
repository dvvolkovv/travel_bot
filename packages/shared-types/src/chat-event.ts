export type ChatEventType =
  | 'thinking'
  | 'tool_call'
  | 'tool_result'
  | 'token'
  | 'cards'
  | 'done'
  | 'error';

export interface ChatEvent<T = unknown> {
  type: ChatEventType;
  data: T;
}

export interface ThinkingEvent { text: string; }
export interface ToolCallEvent { name: string; input: Record<string, unknown>; }
export interface ToolResultEvent { name: string; summary: string; fallback_used?: boolean; }
export interface TokenEvent { text: string; }
export interface CardsEvent { offers: import('./hotel-offer').HotelOffer[]; }
export interface DoneEvent { message_id: string; }
export interface ErrorEvent { message: string; code?: string; }
