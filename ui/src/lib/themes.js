export const THEMES = [
  { id: 'gold', name: 'Aerostar Gold', accent: '#DBBB5E', rgb: '219, 187, 94' },
  { id: 'azure', name: 'Aerostar Blue', accent: '#3891F8', rgb: '56, 145, 248' },
  { id: 'caduceus', name: 'Caduceus', accent: '#00C396', rgb: '0, 195, 150' },
  { id: 'enforcer', name: 'Enforcer', accent: '#C81E28', rgb: '200, 30, 40' },
];

export function applyTheme(id) {
  const t = THEMES.find((x) => x.id === id) || THEMES[0];
  const root = document.documentElement;
  root.style.setProperty('--accent', t.accent);
  root.style.setProperty('--accent-rgb', t.rgb);
  return t;
}
