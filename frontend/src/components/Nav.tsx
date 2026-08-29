function Nav() {
  return (
    <header className="nav" style={{ padding: '14px 28px', boxShadow: 'inset 0 -1px 0 color-mix(in srgb, var(--color-text) 10%, transparent)' }}>
      <a
        href="#/"
        className="nav-brand"
        style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: 'var(--color-text)' }}
      >
        <span
          style={{
            width: 9,
            height: 9,
            borderRadius: 2,
            background: 'var(--color-accent)',
            boxShadow: '0 0 12px var(--color-accent)',
          }}
        />
        Basket Case
      </a>
    </header>
  );
}

export default Nav;
