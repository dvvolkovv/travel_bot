'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

export function AgentTrace({ trace, isStreaming }: { trace: string[]; isStreaming: boolean }) {
  const t = useTranslations('chat');
  const [expanded, setExpanded] = useState(isStreaming);

  useEffect(() => { if (!isStreaming) setExpanded(false); }, [isStreaming]);

  if (trace.length === 0) return null;

  if (isStreaming) {
    return (
      <div className="text-sm text-zinc-500 space-y-1 mb-2">
        {trace.map((line, i) => <div key={i}>{line}</div>)}
      </div>
    );
  }

  return (
    <div className="text-sm text-zinc-500 mb-2">
      <button onClick={() => setExpanded(!expanded)} className="text-xs hover:text-zinc-300">
        {expanded ? `▾ ${t('hide_reasoning')}` : `▸ ${t('show_reasoning')}`}
      </button>
      {expanded && (
        <div className="mt-1 pl-3 border-l border-zinc-800 space-y-1">
          {trace.map((line, i) => <div key={i}>{line}</div>)}
        </div>
      )}
    </div>
  );
}
