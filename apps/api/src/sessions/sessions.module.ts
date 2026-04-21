import { Module } from '@nestjs/common';
import { RedisProvider } from './redis.provider';
import { SessionsService } from './sessions.service';

@Module({
  providers: [RedisProvider, SessionsService],
  exports: [SessionsService],
})
export class SessionsModule {}
