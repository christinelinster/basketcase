import React, { useState } from 'react';
import { Link } from 'react-router-dom';

interface LandingPageProps {
  baskets: string[];
  onCreate: (name: string) => void;
}

function LandingPage({ baskets, onCreate }: LandingPageProps) {
  // Generate random basket name
  const [ newBasketName, setNewBasketName ] = useState(generateBasketName());

  // Event Handlers
  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value

    // 1-50 characters, alphanumeric only
    setNewBasketName(inputValue.replace(/[^a-zA-Z0-9]/g, '').slice(0, 50))
  }

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();

    const basketName = newBasketName.trim()
    if (!basketName) return

    onCreate(basketName);
  }

  // Styles
  const mainStyle = {
    flex: 1, display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 300px', 
    gap: 28, alignItems: 'start', padding: '56px 28px', maxWidth: 1080,
    width: '100%', margin: '0 auto',
  }
  const textBoxStyle = {
    display: 'flex', alignItems: 'stretch', flex: 1, minWidth: 280,
    border: '1px solid var(--color-divider)', borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg)', overflow: 'hidden'
  }
  const basketLinkStyle = {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    gap: 8, padding: '7px 8px', borderRadius: 'var(--radius-sm)', textDecoration: 'none',
    color: 'var(--color-accent-300)', fontSize: 13,
  }

  return (
    <main style={mainStyle}>
      {/* New Basket Card */}
      <section className="card elev-sm" style={{ padding: '28px 28px 24px', gap: 0 }}>
        <h3 style={{ margin: '0 0 6px' }}>New Basket</h3>
        
        <p className="text-muted" style={{ fontSize: 13, margin: '0 0 20px' }}>
          Create a basket to collect and inspect HTTP requests.
        </p>

        {/* Create New Basket Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'stretch', gap: 8, flexWrap: 'wrap' }}>
          <div style={textBoxStyle} >
            <span 
              className="mono text-muted"
              style={{ display: 'flex', alignItems: 'center', padding: '0 2px 0 12px', fontSize: 13, whiteSpace: 'nowrap' }}
            >
              https://basketcase.com/
            </span>

            <input
              className="input mono"
              value={newBasketName}
              onChange={handleNameChange} 
              spellCheck={false}
              style={{ border: 0, background: 'transparent', borderRadius: 0, paddingLeft: 0, fontSize: 13, letterSpacing: '0.04em' }}
            />
            
          </div>
          <button type="submit" className="btn btn-primary" style={{ paddingInline: 20 }}>
            Create
          </button>
        </form>
      </section>

      {/* Baskets List Card */}
      <aside className="card elev-sm" style={{ padding: 0, gap: 0, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', padding: '14px 16px 10px' }}>
          <h6 style={{ margin: 0 }}>My Baskets</h6>
          <span className="text-muted mono" style={{ fontSize: 11 }}>
            {baskets.length ? String(baskets.length) : ''}
          </span>
        </div>

        {/* Basket List Items */}
        <div style={{ maxHeight: 340, overflowY: 'auto', padding: '0 8px 10px' }}>
          { baskets.map(name => (
            <Link key={name} to={`/baskets/${name}`} className="mono bskt" style={basketLinkStyle} >
              <span>{name}</span>
            </Link>
          )) }

          {/* Placeholder Message if the user has no basket tokens stored locally */}
          { !baskets.length && (
            <div className="text-muted" style={{ fontSize: 12, padding: '6px 8px 10px' }}>
              No baskets yet. Create one to get started.
            </div>
          ) }
        </div>
      </aside>
    </main>
  );
}

// Helper for generating random basket names
const ALPHANUMERIC = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
function generateBasketName() {
  let name = ''
  for (let i = 0; i < 7; i++) {
    const randomChar = ALPHANUMERIC[Math.floor(Math.random() * ALPHANUMERIC.length)]
    name += randomChar
  }

  return name
}

export default LandingPage;
