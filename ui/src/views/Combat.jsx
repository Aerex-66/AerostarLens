import { useEffect, useMemo, useState } from 'react';
import { cn } from '@/lib/cn';

const TABS = ['pvp', 'pve', 'all'];

function timeOf(ts) {
  try {
    return new Date(ts).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return ts;
  }
}

function cleanName(n) {
  return n.length > 28 ? n.slice(0, 26) + '\u2026' : n;
}

export default function Combat() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('pvp');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const d = await window.pywebview?.api?.scan_kills?.();
        if (!cancelled) setData(d || null);
      } catch {
        if (!cancelled) setData(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const events = data?.events || [];
  const shown = useMemo(
    () => (tab === 'all' ? events : events.filter((e) => e.kind === tab)),
    [events, tab]
  );
  const counts = useMemo(() => {
    const c = { pvp: 0, pve: 0, all: events.length };
    for (const e of events) if (c[e.kind] !== undefined) c[e.kind] += 1;
    return c;
  }, [events]);

  if (loading) {
    return <p className="py-8 text-center text-[0.68rem] font-light text-slate-500">Reading combat logs…</p>;
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="mb-4 flex gap-1.5">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              'border px-3 py-1.5 text-[0.6rem] font-light uppercase tracking-[0.25em] transition',
              tab === t
                ? 'border-[color:var(--accent)]/50 bg-[rgba(var(--accent-rgb),0.1)] text-[color:var(--accent)]'
                : 'border-white/10 text-slate-500 hover:text-slate-300'
            )}
          >
            {t} · {counts[t]}
          </button>
        ))}
      </div>

      {shown.length === 0 ? (
        <p className="py-8 text-center text-[0.66rem] font-light leading-relaxed text-slate-500">
          No {tab === 'all' ? 'combat' : tab.toUpperCase()} events in this patch&apos;s logs yet.
          <br />
          Kills and deaths appear here as they happen in your sessions.
        </p>
      ) : (
        <div className="divide-y divide-white/5">
          {shown.slice(0, 80).map((e, i) => (
            <div key={i} className="py-2.5">
              <div className="flex items-baseline justify-between gap-3">
                <span className="min-w-0 truncate text-[0.76rem] font-light">
                  <span className={e.killer_is_npc ? 'text-slate-400' : 'text-[color:var(--accent)]'}>
                    {cleanName(e.killer)}
                  </span>
                  <span className="text-slate-600"> → </span>
                  <span className={e.victim_is_npc ? 'text-slate-400' : 'text-slate-200'}>
                    {cleanName(e.victim)}
                  </span>
                </span>
                <span className="shrink-0 text-[0.56rem] font-light text-slate-600">{timeOf(e.at)}</span>
              </div>
              <div className="mt-0.5 truncate text-[0.6rem] font-light text-slate-500">
                {e.damage}
                {e.zone ? ` · ${cleanName(e.zone)}` : ''}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
