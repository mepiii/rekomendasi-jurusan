export const THEME_KEY = 'apti-theme';
export const defaultTheme = 'light';
const validThemes = new Set(['light', 'dark']);

export function loadTheme() {
  const stored = window.localStorage.getItem(THEME_KEY);
  return validThemes.has(stored) ? stored : defaultTheme;
}

export function saveTheme(theme) {
  const nextTheme = validThemes.has(theme) ? theme : defaultTheme;
  window.localStorage.setItem(THEME_KEY, nextTheme);
  return nextTheme;
}

export function toggleTheme(theme) {
  return theme === 'dark' ? 'light' : 'dark';
}
