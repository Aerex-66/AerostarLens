import { THEMES } from '@/lib/themes';

const ACTIONS = ['apply', 'combat', 'configure', 'export'];

export default function Home({ onNavigate, applied, theme, onTheme }) {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-8 py-10">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div
          className="absolute -left-24 top-2 h-72 w-72 animate-float-glow blur-[130px]"
          style={{ background: 'rgba(var(--accent-rgb), 0.16)' }}
        />
        <div className="absolute -right-20 bottom-2 h-72 w-72 animate-float-glow bg-azure-500/10 blur-[130px]" />
      </div>

      <div className="relative mb-11 flex flex-col items-center">
        <div className="relative mb-4">
          <div
            aria-hidden
            className="absolute inset-0 blur-2xl transition-all duration-700"
            style={{ background: applied ? 'rgba(52, 211, 153, 0.4)' : 'rgba(var(--accent-rgb), 0.3)' }}
          />
          <img src="/aerostar-icon.svg" alt="Aerostar" className="relative h-16 w-16" />
        </div>
        <div
          className={`text-sm font-thin tracking-[0.5em] transition-colors duration-500 ${
            applied ? 'text-emerald-300' : 'brushed-gold'
          }`}
        >
          AEROSTAR&nbsp;LENS
        </div>
        {applied && (
          <div className="animate-fade-up mt-2 text-[0.6rem] font-light uppercase tracking-[0.45em] text-emerald-300/90">
            Confirmed
          </div>
        )}
      </div>

      <div className="flex flex-col items-center gap-6">
        {ACTIONS.map((id) => (
          <button key={id} onClick={() => onNavigate(id)} className="group relative px-2 py-1">
            <span className="text-xs font-light uppercase tracking-[0.4em] text-slate-300 transition-colors duration-300 group-hover:text-[color:var(--accent)]">
              {id}
            </span>
            <svg
              aria-hidden
              className="absolute -bottom-1.5 left-0 h-[3px] w-full overflow-visible"
              viewBox="0 0 100 3"
              preserveAspectRatio="none"
            >
              <line
                x1="0"
                y1="1.5"
                x2="100"
                y2="1.5"
                pathLength="1"
                strokeWidth="1.5"
                stroke="var(--accent)"
                className="underline-draw"
              />
            </svg>
          </button>
        ))}
      </div>

      <div className="mt-14 flex items-center gap-3">
        {THEMES.map((t) => (
          <button
            key={t.id}
            onClick={() => onTheme(t.id)}
            title={t.name}
            aria-label={t.name}
            className={`h-2.5 w-2.5 rounded-full border transition ${
              theme === t.id ? 'scale-125 border-white/50' : 'border-white/10 opacity-60 hover:opacity-100'
            }`}
            style={{ background: t.accent }}
          />
        ))}
      </div>
    </div>
  );
}
