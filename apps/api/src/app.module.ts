import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HealthController } from './health/health.controller';
import { PrismaModule } from './prisma/prisma.module';
import { SessionsModule } from './sessions/sessions.module';
import { ChatModule } from './chat/chat.module';
import { RedirectModule } from './redirect/redirect.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule,
    SessionsModule,
    ChatModule,
    RedirectModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
