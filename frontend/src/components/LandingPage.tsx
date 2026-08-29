import { useState } from 'react';
import { Link } from 'react-router-dom';
import { makeToken } from '../lib/token';

interface LandingPageProps {
  baskets: string[];
  onCreate: (name: string) => void;
}

function LandingPage({ baskets, onCreate }: LandingPageProps) {
  const [token, setToken] = useState(makeToken());

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const t = (token || makeToken()).trim();
    if (!t) return;
    onCreate(t);
  };

  return (
    <main
      style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'minmax(0,1fr) 300px',
        gap: 28,
        alignItems: 'start',
        padding: '56px 28px',
        maxWidth: 1080,
        width: '100%',
        margin: '0 auto',
      }}
    >
      <section className="card elev-sm" style={{ padding: '28px 28px 24px', gap: 0 }}>
        <h3 style={{ margin: '0 0 6px' }}>New Basket</h3>
        <p className="text-muted" style={{ fontSize: 13, margin: '0 0 20px' }}>
          Create a basket to collect and inspect HTTP requests.
        </p>
        <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'stretch', gap: 8, flexWrap: 'wrap' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'stretch',
              flex: 1,
              minWidth: 280,
              border: '1px solid var(--color-divider)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-bg)',
              overflow: 'hidden',
            }}
          >
            <span
              className="mono text-muted"
              style={{ display: 'flex', alignItems: 'center', padding: '0 2px 0 12px', fontSize: 13, whiteSpace: 'nowrap' }}
            >
              https://basketcase.com/
            </span>
            <input
              className="input mono"
              value={token}
              onChange={(e) => setToken(e.target.value.replace(/[^a-zA-Z0-9]/g, '').slice(0, 12))}
              spellCheck={false}
              style={{ border: 0, background: 'transparent', borderRadius: 0, paddingLeft: 0, fontSize: 13, letterSpacing: '0.04em' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ paddingInline: 20 }}>
            Create
          </button>
        </form>
      </section>

      <aside className="card elev-sm" style={{ padding: 0, gap: 0, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', padding: '14px 16px 10px' }}>
          <h6 style={{ margin: 0 }}>My Baskets</h6>
          <span className="text-muted mono" style={{ fontSize: 11 }}>
            {baskets.length ? String(baskets.length) : ''}
          </span>
        </div>
        <div style={{ maxHeight: 340, overflowY: 'auto', padding: '0 8px 10px' }}>
          {baskets.map(name => (
            <Link
              key={name}
              to={`/baskets/${name}`}
              className="mono bskt"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 8,
                padding: '7px 8px',
                borderRadius: 'var(--radius-sm)',
                textDecoration: 'none',
                color: 'var(--color-accent-300)',
                fontSize: 13,
              }}
            >
              <span>{name}</span>
            </Link>
          ))}
          {!baskets.length && (
            <div className="text-muted" style={{ fontSize: 12, padding: '6px 8px 10px' }}>
              No baskets yet. Create one to get started.
            </div>
          )}
        </div>
      </aside>
    </main>
  );
}

export default LandingPage;
