const CHANNEL_NAMES = ['LIVE', 'PTU', 'EPTU', 'HOTFIX', 'TECH-PREVIEW'];

export function channelFromPath(p) {
  if (!p) return null;
  const segs = String(p).split(/[\\/]+/).map((s) => s.toUpperCase());
  return CHANNEL_NAMES.find((c) => segs.includes(c)) || null;
}
