import { Inject, Injectable } from '@nestjs/common';
import Redis from 'ioredis';
import { REDIS } from './redis.provider';

export interface ChatSessionData {
  messages: Array<{ role: 'user' | 'assistant'; content: unknown }>;
  lang: 'en' | 'ru';
  currency: string;
  createdAt: string;
}

const TTL_SECONDS = 7200;

@Injectable()
export class SessionsService {
  constructor(@Inject(REDIS) private readonly redis: Redis) {}

  private key(sessionId: string): string {
    return `chat:${sessionId}`;
  }

  async get(sessionId: string): Promise<ChatSessionData | null> {
    const raw = await this.redis.get(this.key(sessionId));
    return raw ? JSON.parse(raw) : null;
  }

  async create(
    sessionId: string,
    lang: 'en' | 'ru',
    currency: string,
  ): Promise<ChatSessionData> {
    const data: ChatSessionData = {
      messages: [],
      lang,
      currency,
      createdAt: new Date().toISOString(),
    };
    await this.redis.set(this.key(sessionId), JSON.stringify(data), 'EX', TTL_SECONDS);
    return data;
  }

  async appendMessage(
    sessionId: string,
    message: { role: 'user' | 'assistant'; content: unknown },
  ): Promise<void> {
    const existing = await this.get(sessionId);
    if (!existing) throw new Error(`session not found: ${sessionId}`);
    existing.messages.push(message);
    await this.redis.set(this.key(sessionId), JSON.stringify(existing), 'EX', TTL_SECONDS);
  }

  async delete(sessionId: string): Promise<void> {
    await this.redis.del(this.key(sessionId));
  }
}
