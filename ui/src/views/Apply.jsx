import { useState } from 'react';
import { Check } from 'lucide-react';
import { CATEGORIES } from '@/data/mock';
import { cn } from '@/lib/cn';

export default function Apply({ install, channel, onApplied }) {
  const [cats, setCats] = useState(CATEGORIES);
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState(null);
  const toggle = (id) =>
    setCats((cs) => cs.map((c) => (c.id === id && c.ready ? { ...c, enabled: !c.enabled } : c)));
  const enabled = cats.filter((c) => c.enabled && c.ready).map((c) => c.id);

  const handleApply = async () => {
    if (!install) {
      setMessage('Set your Star Citizen install in Configure first.');
      return;
    }
    setStatus('applying');
    setMessage(null);
    const poll = setInterval(async () => {
      try {
        const p = await window.pywebview?.api?.get_progress?.();
        if (p) setMessage(p);
      } catch {
      }
    }, 700);
    try {
      const res = await window.pywebview?.api?.apply_enhancements?.(install, channel, enabled);
      if (res?.ok) {
        setStatus('done');
        setMessage(`${res.enhanced_keys} strings enhanced. Backup saved.`);
        onApplied?.();
      } else {
        setStatus('idle');
        setMessage(res?.error || 'Apply failed.');
      }
    } catch {
      setStatus('idle');
      setMessage('Apply failed - desktop bridge unavailable.');
    } finally {
      clearInterval(poll);
    }
  };

  const handleRestore = async () => {
    if (!install) return;
    try {
      const res = await window.pywebview?.api?.restore_localization?.(install, channel);
      setStatus('idle');
      setMessage(res?.ok ? `Restored: ${res.restored}` : res?.error || 'Restore failed.');
    } catch {
      setMessage('Restore failed - desktop bridge unavailable.');
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <p className="mb-4 text-center text-[0.62rem] font-light leading-relaxed text-slate-500">
        A backup is taken before anything changes.
      </p>

      <div className="divide-y divide-white/5">
        {cats.map((c) => (
          <button
            key={c.id}
            onClick={() => toggle(c.id)}
            disabled={!c.ready}
            className={cn(
              'group flex w-full items-center gap-3 py-2.5 text-left',
              !c.ready && 'cursor-not-allowed opacity-40'
            )}
          >
            <span
              className={cn(
                'grid h-4 w-4 shrink-0 place-items-center border transition',
                c.enabled && c.ready
                  ? 'border-[color:var(--accent)] bg-[rgba(var(--accent-rgb),0.15)]'
                  : 'border-white/15 group-hover:border-white/30'
              )}
            >
              {c.enabled && c.ready && <Check size={10} strokeWidth={2.5} className="text-[color:var(--accent)]" />}
            </span>
            <span className="min-w-0 flex-1">
              <span className={cn('block truncate text-[0.78rem]', c.enabled && c.ready ? 'text-white' : 'text-slate-400')}>
                {c.name}
                {!c.ready && <span className="ml-2 text-[0.5rem] uppercase tracking-wider text-slate-600">soon</span>}
              </span>
              <span className="block truncate text-[0.62rem] font-light text-slate-500">{c.desc}</span>
            </span>
          </button>
        ))}
      </div>

      <div className="mt-5 flex flex-col items-center gap-2.5">
        <div className="flex items-center justify-center gap-5">
          <button
            onClick={handleApply}
            disabled={status === 'applying' || enabled.length === 0}
            className="inline-flex items-center gap-2 border border-[color:var(--accent)]/40 bg-[rgba(var(--accent-rgb),0.08)] px-6 py-2 text-[0.64rem] font-light uppercase tracking-[0.3em] text-[color:var(--accent)] transition hover:bg-[rgba(var(--accent-rgb),0.16)] disabled:opacity-50"
          >
            {status === 'done' && <Check size={12} />}
            {status === 'applying' ? 'Applying' : status === 'done' ? 'Applied' : `Apply · ${enabled.length}`}
          </button>
          <button
            onClick={handleRestore}
            className="text-[0.64rem] font-light uppercase tracking-[0.2em] text-slate-500 transition hover:text-slate-300"
          >
            Restore
          </button>
        </div>
        {message && (
          <p className="flex items-center gap-2 text-center text-[0.62rem] font-light text-slate-400">
            {status === 'applying' && (
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--accent)]" />
            )}
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
