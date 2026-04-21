import { Module } from '@nestjs/common';
import { SessionsModule } from '../sessions/sessions.module';
import { ChatController } from './chat.controller';

@Module({
  imports: [SessionsModule],
  controllers: [ChatController],
})
export class ChatModule {}
