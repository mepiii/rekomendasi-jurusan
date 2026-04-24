// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest';
import {
  THEME_KEY,
  defaultTheme,
  loadTheme,
  saveTheme,
  toggleTheme,
} from './themeState';

describe('themeState', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('defaults to light when storage is empty', () => {
    expect(THEME_KEY).toBe('apti-theme');
    expect(defaultTheme).toBe('light');
    expect(loadTheme()).toBe('light');
  });

  it('saves and loads dark theme', () => {
    expect(saveTheme('dark')).toBe('dark');
    expect(window.localStorage.getItem(THEME_KEY)).toBe('dark');
    expect(loadTheme()).toBe('dark');
  });

  it('falls back to light for invalid stored values', () => {
    window.localStorage.setItem(THEME_KEY, 'system');

    expect(loadTheme()).toBe('light');
    expect(saveTheme('system')).toBe('light');
    expect(window.localStorage.getItem(THEME_KEY)).toBe('light');
  });

  it('toggles between light and dark', () => {
    expect(toggleTheme('light')).toBe('dark');
    expect(toggleTheme('dark')).toBe('light');
  });
});
