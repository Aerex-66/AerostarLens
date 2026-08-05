import { useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { THEMES } from '@/lib/themes';
import { cn } from '@/lib/cn';

const LANGUAGES = ['English', 'Français', 'Español', 'Português (BR)'];

function Group({ title, children }) {
  return (
    <div>
      <p className="mb-1 text-[0.55rem] font-light uppercase tracking-[0.35em] text-slate-500">{title}</p>
      <div className="divide-y divide-white/5">{children}</div>
    </div>
  );
}

function Row({ label, hint, children }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2.5">
      <div className="min-w-0">
        <p className="truncate text-[0.78rem] font-light text-slate-200">{label}</p>
        {hint && <p className="mt-0.5 truncate text-[0.6rem] font-light text-slate-500">{hint}</p>}
      </div>
      <div className="shrink-0 text-right">{children}</div>
    </div>
  );
}

function PathBtn({ value, placeholder, onClick }) {
  return (
    <button onClick={onClick} className="group flex items-center gap-1.5">
      <span className="max-w-[150px] truncate font-mono text-[0.58rem] text-slate-400">
        {value || placeholder}
      </span>
      <FolderOpen size={12} className="shrink-0 text-slate-500 transition group-hover:text-[color:var(--accent)]" />
    </button>
  );
}

export default function Config({ install, onInstall, channel, detectDone, theme, onTheme }) {
  const [lang, setLang] = useState('English');
  const [dataFolder, setDataFolder] = useState('Documents\\AerostarLens');

  const pickFolder = async (setter) => {
    try {
      const picked = await window.pywebview?.api?.pick_folder?.();
      if (picked) setter(picked);
    } catch {
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-5">
      <Group title="Game">
        <Row label="Star Citizen install" hint="Auto-detected — pick a LIVE / PTU / TECH-PREVIEW folder to override">
          <PathBtn
            value={install}
            placeholder={detectDone ? 'Not found — pick folder' : 'Detecting…'}
            onClick={() => pickFolder(onInstall)}
          />
        </Row>
        <Row label="Active channel" hint="Detected from the install folder">
          <span className={channel ? 'text-sm font-light text-[color:var(--accent)]' : 'text-xs text-slate-500'}>
            {channel || 'Not set'}
          </span>
        </Row>
        <Row label="Language" hint="App + in-game strings">
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            className="border border-white/10 bg-white/[0.03] px-2 py-1 text-xs font-light text-slate-200 focus:outline-none"
          >
            {LANGUAGES.map((l) => (
              <option key={l} className="bg-ink-900">
                {l}
              </option>
            ))}
          </select>
        </Row>
      </Group>

      <Group title="Storage">
        <Row label="Data folder" hint="Where exports and settings live">
          <PathBtn value={dataFolder} onClick={() => pickFolder(setDataFolder)} />
        </Row>
      </Group>

      <div>
        <p className="mb-3 text-[0.55rem] font-light uppercase tracking-[0.35em] text-slate-500">Theme</p>
        <div className="flex flex-wrap gap-5">
          {THEMES.map((t) => (
            <button key={t.id} onClick={() => onTheme(t.id)} className="flex flex-col items-center gap-2">
              <span
                className={cn(
                  'h-7 w-7 rounded-full border transition',
                  theme === t.id ? 'scale-110 border-white/60' : 'border-white/10 hover:border-white/30'
                )}
                style={{ background: t.accent }}
              />
              <span
                className={cn(
                  'text-[0.58rem] font-light uppercase tracking-wider',
                  theme === t.id ? 'text-slate-200' : 'text-slate-500'
                )}
              >
                {t.name.replace('Aerostar ', '')}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
