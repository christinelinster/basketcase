import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import type { CreatedBasket } from '../types/basket';

interface LandingPageProps {
  baskets: string[];
  createdBasket: CreatedBasket | null;
  onCreate: (name: string) => Promise<void>;
}

function LandingPage({ baskets, createdBasket, onCreate }: LandingPageProps) {
  // Generate random basket name
  const [ newBasketName, setNewBasketName ] = useState(generateBasketName());
  const [ copied, setCopied ] = useState(false);

  // Event Handlers
  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value

    // 1-50 characters, alphanumeric only
    setNewBasketName(inputValue.replace(/[^a-zA-Z0-9]/g, '').slice(0, 50))
  }

  const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();

    const basketName = newBasketName.trim()
    if (!basketName) return

    setCopied(false)
    await onCreate(basketName);
  }

  const copyWebhookUrl = async () => {
    if (!createdBasket || !navigator.clipboard) return

    await navigator.clipboard.writeText(createdBasket.webhook_url)
    setCopied(true)
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

        {createdBasket && (
          <div style={{ marginTop: 18, padding: 14, borderRadius: 'var(--radius-md)', background: 'var(--color-bg)', boxShadow: 'inset 0 0 0 1px var(--color-accent-800)' }}>
            <div className="text-muted" style={{ fontSize: 12, marginBottom: 7 }}>
              Send webhook requests to
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span className="mono" style={{ color: 'var(--color-accent-200)', fontSize: 13, overflowWrap: 'anywhere' }}>
                {createdBasket.webhook_url}
              </span>
              <button type="button" className="btn btn-secondary" onClick={copyWebhookUrl}>
                Copy URL
              </button>
              {copied && <span style={{ color: 'var(--color-accent)', fontSize: 12 }}>Copied</span>}
            </div>
          </div>
        )}
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
