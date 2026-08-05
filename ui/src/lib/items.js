import NAMES from '@/data/item_names.json';

export function prettify(cls) {
  return cls
    .replace(/_/g, ' ')
    .replace(/\b\d{2,}\b/g, '') // drop numeric variant chunks
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function resolve(cls) {
  const hit = NAMES[cls];
  return {
    name: hit?.name || prettify(cls),
    manufacturer: hit?.manufacturer || '',
    type: hit?.type || '',
    resolved: Boolean(hit),
  };
}
