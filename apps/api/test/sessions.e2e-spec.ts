import { Test } from '@nestjs/testing';
import { ConfigModule } from '@nestjs/config';
import { SessionsModule } from '../src/sessions/sessions.module';
import { SessionsService } from '../src/sessions/sessions.service';
import { REDIS } from '../src/sessions/redis.provider';
import type Redis from 'ioredis';

describe('SessionsService', () => {
  let service: SessionsService;
  let redis: Redis;

  beforeAll(async () => {
    const mod = await Test.createTestingModule({
      imports: [ConfigModule.forRoot({ isGlobal: true }), SessionsModule],
    }).compile();
    service = mod.get(SessionsService);
    redis = mod.get(REDIS);
  });

  afterAll(async () => {
    await redis.quit();
  });

  it('creates, reads, and appends messages', async () => {
    const sid = `test-${Date.now()}`;
    await service.create(sid, 'en', 'USD');

    const initial = await service.get(sid);
    expect(initial?.messages).toEqual([]);
    expect(initial?.lang).toBe('en');

    await service.appendMessage(sid, { role: 'user', content: 'hello' });
    const after = await service.get(sid);
    expect(after?.messages).toHaveLength(1);

    await service.delete(sid);
    const gone = await service.get(sid);
    expect(gone).toBeNull();
  });
});
