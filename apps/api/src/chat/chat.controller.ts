import { Body, Controller, Post, Req, Res } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Request, Response } from 'express';
import { SessionsService } from '../sessions/sessions.service';
import { detectCurrency, detectLang } from './language-detect';

interface TurnBody {
  session_id: string;
  message: string;
}

@Controller('chat')
export class ChatController {
  constructor(
    private readonly sessions: SessionsService,
    private readonly config: ConfigService,
  ) {}

  @Post('turn')
  async turn(@Body() body: TurnBody, @Req() req: Request, @Res() res: Response) {
    const { session_id, message } = body;
    if (!session_id || !message) {
      res.status(400).json({ error: 'session_id and message required' });
      return;
    }

    let session = await this.sessions.get(session_id);
    if (!session) {
      const lang = detectLang(message);
      const currency = detectCurrency(message, lang);
      session = await this.sessions.create(session_id, lang, currency);
    }

    const agentUrl = this.config.get<string>('AI_AGENT_BASE_URL') ?? 'http://localhost:8001';
    const upstreamResp = await fetch(`${agentUrl}/agent/turn`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        session_id,
        message,
        history: session.messages,
        lang: session.lang,
        currency: session.currency,
      }),
    });

    if (!upstreamResp.ok || !upstreamResp.body) {
      res.status(502).json({ error: 'ai-agent unavailable' });
      return;
    }

    res.setHeader('content-type', 'text/event-stream');
    res.setHeader('cache-control', 'no-cache');
    res.setHeader('connection', 'keep-alive');
    res.flushHeaders();

    await this.sessions.appendMessage(session_id, { role: 'user', content: message });

    const reader = upstreamResp.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(decoder.decode(value, { stream: true }));
    }
    res.end();
  }
}
