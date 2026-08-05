import { useState } from 'react';
import { Check, Download } from 'lucide-react';
import Inventory from '@/views/Inventory';

export default function Export() {
  const [state, setState] = useState('idle'); // idle | saving | done
  const [path, setPath] = useState(null);

  const handleExport = async () => {
    setState('saving');
    try {
      const dest = await window.pywebview?.api?.export_inventory?.();
      setPath(dest || null);
      setState(dest ? 'done' : 'idle');
    } catch {
      setState('idle');
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-7">
      <div className="flex flex-col items-center gap-2 text-center">
        <button
          onClick={handleExport}
          disabled={state === 'saving'}
          className="inline-flex items-center gap-2 border border-[color:var(--accent)]/40 bg-[rgba(var(--accent-rgb),0.08)] px-7 py-2.5 text-[0.7rem] font-light uppercase tracking-[0.3em] text-[color:var(--accent)] transition hover:bg-[rgba(var(--accent-rgb),0.16)] disabled:opacity-50"
        >
          {state === 'done' ? <Check size={13} /> : <Download size={13} />}
          {state === 'saving' ? 'Exporting' : state === 'done' ? 'Exported' : 'Export to file'}
        </button>
        {path && <p className="max-w-full truncate font-mono text-[0.6rem] text-slate-500">{path}</p>}
        <p className="text-[0.66rem] font-light text-slate-500">
          Everything stays on this machine unless you share the file.
        </p>
      </div>

      <Inventory />
    </div>
  );
}
