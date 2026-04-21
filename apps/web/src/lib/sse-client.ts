import type { ChatEventType } from '@hotel-deals/shared-types';

export interface SseClientOptions {
  url: string;
  body: unknown;
  onEvent: (type: ChatEventType, data: unknown) => void;
  onDone: () => void;
  onError: (err: unknown) => void;
}

export async function streamTurn(opts: SseClientOptions): Promise<void> {
  const resp = await fetch(opts.url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(opts.body),
  });
  if (!resp.ok || !resp.body) {
    opts.onError(new Error(`HTTP ${resp.status}`));
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() ?? '';
    for (const raw of events) {
      const typeMatch = raw.match(/^event: (\w+)/m);
      const dataMatch = raw.match(/^data: (.+)$/m);
      if (!typeMatch || !dataMatch) continue;
      try {
        opts.onEvent(typeMatch[1] as ChatEventType, JSON.parse(dataMatch[1]));
      } catch (e) {
        opts.onError(e);
      }
    }
  }
  opts.onDone();
}
