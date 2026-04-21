'use client';

import type { HotelOffer } from '@hotel-deals/shared-types';
import { AgentTrace } from './AgentTrace';
import { HotelCard } from './HotelCard';

export function AssistantMessage({
  text, trace, offers, isStreaming = false,
}: {
  text: string;
  trace?: string[];
  offers?: HotelOffer[];
  isStreaming?: boolean;
}) {
  return (
    <div className="space-y-3">
      {trace && <AgentTrace trace={trace} isStreaming={isStreaming} />}
      {text && <div className="whitespace-pre-wrap">{text}</div>}
      {offers && offers.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {offers.map((o) => (
            <div key={o.offer_id} data-testid="hotel-card">
              <HotelCard offer={o} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
