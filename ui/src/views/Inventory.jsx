import { useEffect, useMemo, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { resolve } from '@/lib/items';
import { cn } from '@/lib/cn';

function typeOf(cls) {
  if (/undersuit/i.test(cls)) return 'Undersuits';
  if (/_mag$|magazine|_ammo/i.test(cls)) return 'Magazines';
  if (/optics|scope|ubarrel|barrel|flsh|sight|tint/i.test(cls)) return 'Optics & Attachments';
  if (/helmet|_core|_arms|_legs|backpack|mask|_torso|armor|_suit/i.test(cls)) return 'Armor';
  if (/medpen|consumable|oxypen|vial|painkiller|adrenal|medgun/i.test(cls)) return 'Medical & Consumables';
  if (/gren|frag|grenade/i.test(cls)) return 'Ordnance';
  if (/rifle|pistol|smg|lmg|hmg|sniper|shotgun|multitool|weapon|crossbow/i.test(cls)) return 'Weapons';
  if (/tool|tractor|mining|salvage/i.test(cls)) return 'Tools';
  if (/keycard|scrip|currency|\bkey\b/i.test(cls)) return 'Keys & Currency';
  return 'Other';
}

export default function Inventory() {
  const [snap, setSnap] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await window.pywebview?.api?.scan_inventory?.();
        if (!cancelled) setSnap(data || null);
      } catch {
        if (!cancelled) setSnap(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const { cats, total } = useMemo(() => {
    const byCat = {};
    for (const [cls, g] of Object.entries(snap?.items_by_class || {})) {
      const t = typeOf(cls);
      const bucket = (byCat[t] = byCat[t] || { qty: 0, items: [] });
      bucket.qty += g.count || 0;
      bucket.items.push({ name: resolve(cls).name, qty: g.count || 0 });
    }
    const catList = Object.entries(byCat)
      .map(([name, b]) => ({ name, qty: b.qty, items: b.items.sort((a, z) => z.qty - a.qty) }))
      .sort((a, z) => z.qty - a.qty);
    return { cats: catList, total: catList.reduce((s, c) => s + c.qty, 0) };
  }, [snap]);

  const max = Math.max(1, ...cats.map((c) => c.qty));
  const purchases = snap?.purchases || [];
  const spent = purchases.filter((p) => p.kind === 'buy').reduce((s, p) => s + (p.price || 0), 0);
  const missionsDone = snap?.missions_completed || 0;

  if (loading) {
    return <p className="py-8 text-center text-[0.68rem] font-light text-slate-500">Scanning your game logs…</p>;
  }
  if (!cats.length) {
    return (
      <p className="py-8 text-center text-[0.68rem] font-light leading-relaxed text-slate-500">
        Nothing captured yet. Play a session, then come back —<br />
        items are collected as you handle them in game.
      </p>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-baseline justify-between">
        <p className="text-[0.55rem] font-light uppercase tracking-[0.35em] text-slate-500">
          Inventory{snap?.patch ? ` · ${snap.patch}` : ''}
        </p>
        <p className="text-[0.66rem] font-light text-slate-400">
          <span className="text-[color:var(--accent)]">{total}</span> total qty
        </p>
      </div>

      <div className="divide-y divide-white/5">
        {cats.map((c) => (
          <CategoryRow key={c.name} c={c} max={max} />
        ))}
      </div>

      {(purchases.length > 0 || missionsDone > 0) && (
        <div className="mt-5 border-t border-white/10 pt-3">
          <div className="flex items-baseline justify-between text-[0.62rem] font-light text-slate-400">
            <span>
              <span className="text-[color:var(--accent)]">{purchases.length}</span> purchases · spent{' '}
              <span className="text-[color:var(--accent)]">{spent.toLocaleString()}</span> aUEC
            </span>
            <span>
              <span className="text-[color:var(--accent)]">{missionsDone}</span> missions completed
            </span>
          </div>
          <PurchaseList purchases={purchases} />
        </div>
      )}
    </div>
  );
}

function PurchaseList({ purchases }) {
  const [open, setOpen] = useState(false);
  if (!purchases.length) return null;
  const recent = purchases.slice(-8).reverse();
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 text-[0.58rem] font-light uppercase tracking-[0.2em] text-slate-500 transition hover:text-slate-300"
      >
        <ChevronDown size={11} className={cn('transition-transform', open && 'rotate-180')} />
        Recent purchases
      </button>
      {open && (
        <div className="mt-2 divide-y divide-white/5">
          {recent.map((p, i) => (
            <div key={i} className="flex items-baseline justify-between gap-3 py-1.5 text-[0.66rem] font-light">
              <span className="truncate text-slate-300">{resolve(p.item).name}</span>
              <span className="shrink-0 text-slate-500">
                {p.kind === 'sell' ? '+' : '-'}
                {Math.round(p.price).toLocaleString()} aUEC
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CategoryRow({ c, max }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="py-3.5">
      <button onClick={() => setOpen((o) => !o)} className="group w-full text-left">
        <div className="mb-1.5 flex items-baseline justify-between">
          <span className="flex items-center gap-1.5 text-sm font-light text-slate-200">
            <ChevronDown size={12} className={cn('text-slate-500 transition-transform', open && 'rotate-180')} />
            {c.name}
          </span>
          <span className="text-[0.66rem] font-light text-slate-400">
            <span className="text-[color:var(--accent)]">{c.qty}</span> qty
          </span>
        </div>
        <div className="h-px w-full overflow-hidden bg-white/10">
          <div
            className="h-full transition-all duration-500"
            style={{ width: `${(c.qty / max) * 100}%`, background: 'var(--accent)' }}
          />
        </div>
      </button>

      {open && (
        <div className="mt-2.5 divide-y divide-white/5 pl-5">
          {c.items.map((it, i) => (
            <div key={i} className="flex items-baseline justify-between gap-3 py-1.5 text-[0.7rem] font-light">
              <span className="truncate text-slate-300">{it.name}</span>
              <span className="shrink-0 text-slate-500">{it.qty}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
