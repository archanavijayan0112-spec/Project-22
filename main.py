@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Color tokens — atmosphere/grid-intensity palette */
  --bg-base: #0e1a1a;
  --bg-surface: #142524;
  --bg-surface-raised: #1a2f2d;
  --border-subtle: #24403c;

  --text-primary: #eaf2ef;
  --text-secondary: #9db3ac;
  --text-tertiary: #6b8580;

  --accent-cyan: #5fb8b3;
  --accent-cyan-dim: #3d7a76;

  /* Carbon-intensity scale: the app's signature visual language */
  --intensity-clean: #4fc17d;
  --intensity-moderate: #e8b23d;
  --intensity-high: #d9713c;
  --intensity-severe: #c04a3f;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;

  --font-display: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  color-scheme: dark;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}

body {
  background-image:
    radial-gradient(ellipse at top left, rgba(95, 184, 179, 0.06), transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(232, 178, 61, 0.04), transparent 50%);
  background-attachment: fixed;
  min-height: 100vh;
}

h1, h2, h3, h4 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
}

p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

button {
  font-family: var(--font-body);
  cursor: pointer;
}

input, select, textarea {
  font-family: var(--font-body);
}

a {
  color: var(--accent-cyan);
}

::selection {
  background: var(--accent-cyan-dim);
  color: var(--text-primary);
}

/* Focus visibility for accessibility */
button:focus-visible,
input:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 2px solid var(--accent-cyan);
  outline-offset: 2px;
}

.mono {
  font-family: var(--font-mono);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

::-webkit-scrollbar {
  width: 10px;
}
::-webkit-scrollbar-track {
  background: var(--bg-base);
}
::-webkit-scrollbar-thumb {
  background: var(--border-subtle);
  border-radius: 8px;
}
