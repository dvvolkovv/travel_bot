import { Provider } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Redis from 'ioredis';

export const REDIS = Symbol('REDIS');

export const RedisProvider: Provider = {
  provide: REDIS,
  inject: [ConfigService],
  useFactory: (config: ConfigService) => {
    const url = config.get<string>('REDIS_URL') ?? 'redis://localhost:6379';
    return new Redis(url);
  },
};
