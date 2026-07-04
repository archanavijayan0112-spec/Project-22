.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 24px 40px;
  border-bottom: 1px solid var(--border-subtle);
}

.navbar__brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.navbar__mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--intensity-clean), var(--intensity-moderate) 55%, var(--intensity-severe));
}

.navbar__title {
  font-size: 18px;
  color: var(--text-primary);
}

.navbar__subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.navbar__tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-surface);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.navbar__tab {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  transition: background 0.15s ease, color 0.15s ease;
}

.navbar__tab:hover:not(:disabled) {
  color: var(--text-primary);
}

.navbar__tab--active {
  background: var(--bg-surface-raised);
  color: var(--text-primary);
}

.navbar__tab:disabled {
  color: var(--text-tertiary);
  cursor: not-allowed;
  opacity: 0.5;
}

@media (max-width: 720px) {
  .navbar {
    padding: 16px 20px;
  }
  .navbar__tabs {
    width: 100%;
    overflow-x: auto;
  }
}
