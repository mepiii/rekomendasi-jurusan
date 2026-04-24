// Purpose: Provide shared Apti app-shell framing, theme toggle, locale toggle, and optional actions around composed content.
// Callers: App component.
// Deps: React children composition.
// API: Default export AptiShell({ theme, onToggleTheme, locale, onToggleLocale, copy, title, subtitle, actions, children }).
// Side effects: None.
export default function AptiShell({ theme, onToggleTheme, locale, onToggleLocale, copy, title, subtitle, actions = null, children }) {
  const themeLabel = theme === 'dark' ? copy.themeLight : copy.themeDark;
  const nextLocaleLabel = locale === 'en' ? 'ID' : 'EN';

  return (
    <main
      data-testid="apti-shell"
      data-theme={theme}
      className="apti-shell min-h-screen w-full px-4 py-10 sm:px-6 lg:px-8"
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 apti-fade-up">
        <header className="apti-shell-header apti-shimmer flex flex-col gap-4 rounded-3xl p-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-textSubtle">{copy.appName}</p>
            {title ? <h1 className="text-3xl font-semibold tracking-tight text-textPrimary">{title}</h1> : null}
            {subtitle ? <p className="max-w-2xl text-sm text-textMuted">{subtitle}</p> : null}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button type="button" onClick={onToggleLocale} className="apti-secondary-button rounded-xl px-4 py-2 text-sm font-medium">
              {copy.languageLabel}: {nextLocaleLabel}
            </button>
            <button
              type="button"
              onClick={onToggleTheme}
              className="apti-secondary-button rounded-xl px-4 py-2 text-sm font-medium"
            >
              {themeLabel}
            </button>
            {actions}
          </div>
        </header>
        <div className="flex w-full flex-col items-center gap-6">{children}</div>
      </div>
    </main>
  );
}
