import { useEffect, useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import Home from '@/views/Home';
import Apply from '@/views/Apply';
import Combat from '@/views/Combat';
import Config from '@/views/Config';
import Export from '@/views/Export';
import { applyTheme } from '@/lib/themes';
import { channelFromPath } from '@/lib/sc';

const TITLES = { apply: 'Apply', combat: 'Combat', configure: 'Configure', export: 'Export' };

export default function App() {
  const [screen, setScreen] = useState('home');
  const [applied, setApplied] = useState(false);
  const [install, setInstall] = useState(null);
  const [channel, setChannel] = useState(null);
  const [version, setVersion] = useState(null);
  const [theme, setTheme] = useState('gold');

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const [detectDone, setDetectDone] = useState(false);
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      try {
        const info = await window.pywebview?.api?.detect_install?.();
        if (!cancelled && info?.path) setInstall(info.path);
      } catch {
      } finally {
        if (!cancelled) setDetectDone(true);
      }
    };
    if (window.pywebview?.api) {
      run();
    } else {
      const onReady = () => run();
      window.addEventListener('pywebviewready', onReady);
      const late = setTimeout(() => {
        if (window.pywebview?.api && !cancelled) run();
        else if (!cancelled) setDetectDone(true);
      }, 2500);
      return () => {
        cancelled = true;
        clearTimeout(late);
        window.removeEventListener('pywebviewready', onReady);
      };
    }
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!install) return;
    setChannel(channelFromPath(install));
    (async () => {
      try {
        setVersion((await window.pywebview?.api?.game_version?.(install)) || null);
      } catch {
        setVersion(null);
      }
    })();
  }, [install]);

  const [gameOn, setGameOn] = useState(false);
  useEffect(() => {
    let stop = false;
    const check = async () => {
      try {
        const on = await window.pywebview?.api?.game_running?.();
        if (!stop) setGameOn(Boolean(on));
      } catch {
      }
    };
    check();
    const id = setInterval(check, 8000);
    return () => {
      stop = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="relative flex h-screen flex-col overflow-hidden">
      {screen === 'home' && (
        <>
          <div className="pointer-events-none absolute left-4 top-3 z-30 flex items-center gap-1.5 text-[0.58rem] font-light uppercase tracking-[0.25em]">
            <span
              className={gameOn ? 'h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px] shadow-emerald-400/70' : 'h-1.5 w-1.5 rounded-full bg-slate-600'}
            />
            <span className={gameOn ? 'text-emerald-300' : 'text-slate-600'}>
              {gameOn ? 'Game detected' : 'Game offline'}
            </span>
          </div>
          {channel && (
            <div className="pointer-events-none absolute right-4 top-3 z-30 text-[0.58rem] font-light uppercase tracking-[0.25em] text-[color:var(--accent)]">
              {channel}
              {version && <span className="text-slate-500"> · {version}</span>}
            </div>
          )}
        </>
      )}

      {screen === 'home' ? (
        <Home onNavigate={setScreen} applied={applied} theme={theme} onTheme={setTheme} />
      ) : (
        <>
          <header className="flex items-center gap-3 border-b border-white/10 px-5 py-2.5">
            <button
              onClick={() => setScreen('home')}
              className="grid h-7 w-7 place-items-center border border-white/10 text-slate-300 transition hover:border-[color:var(--accent)]/40 hover:text-[color:var(--accent)]"
              aria-label="Back to home"
            >
              <ArrowLeft size={15} />
            </button>
            <h1 className="text-[0.68rem] font-light uppercase tracking-[0.35em] text-white">{TITLES[screen]}</h1>
            <div className="ml-auto flex items-center gap-3 text-[0.55rem] font-light uppercase tracking-[0.2em]">
              <span className={gameOn ? 'text-emerald-300' : 'text-slate-600'}>
                {gameOn ? '\u25cf game' : '\u25cb game'}
              </span>
              {channel && (
                <span className="text-[color:var(--accent)]">
                  {channel}
                  {version && <span className="text-slate-500"> · {version}</span>}
                </span>
              )}
            </div>
          </header>
          <main className="flex-1 overflow-y-auto px-5 py-4">
            <div key={screen} className="mx-auto max-w-3xl animate-fade-up">
              {screen === 'apply' && (
                <Apply install={install} channel={channel} onApplied={() => setApplied(true)} />
              )}
              {screen === 'combat' && <Combat />}
              {screen === 'configure' && (
                <Config
                  install={install}
                  onInstall={setInstall}
                  channel={channel}
                  detectDone={detectDone}
                  theme={theme}
                  onTheme={setTheme}
                />
              )}
              {screen === 'export' && <Export />}
            </div>
          </main>
        </>
      )}
    </div>
  );
}
