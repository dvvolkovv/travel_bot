import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HealthController } from './health/health.controller';
import { PrismaModule } from './prisma/prisma.module';
import { SessionsModule } from './sessions/sessions.module';

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true }), PrismaModule, SessionsModule],
  controllers: [HealthController],
})
export class AppModule {}
