// >> React
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
// > Components
import RequestCard from './RequestCard';
import SVGButton from './SVGButton';
import { ICON_COPY, ICON_LINK, ICON_TRASH } from './icons';
// > Types
import type { BasketRequest } from '../types/basket';
// > Services
import BasketService from '../services/BasketService';
// > Config
import { basketUrl } from '../config';
// > Hooks
import useBasketRefresh from '../hooks/useBasketRefresh';

interface BasketPageProps {
  onDelete: (name: string) => void;
}

function BasketPage({ onDelete }: BasketPageProps) {
  const navigate = useNavigate()
  // State:
  const [ requests, setRequests ] = useState<BasketRequest[]>([]);

  // - Click-to-copy
  const [ copied, setCopied ] = useState('');
  const copyTimer = useRef<number | null>(null);
  // --------------------------------------------------------------
  // 1) Extract :name from URL:
  const { name } = useParams()

  // 2) Load basket & request details:
  useEffect(() => {
    if (name === undefined) {
      navigate('/baskets', { replace: true })
      return
    }

    const loadBasketDetails = async () => {
      try {
        const basket = await BasketService.loadBasketDetails(name)
        setRequests(basket.requests)
      } catch (error) {
        console.error(error)
        alert(`Basket ${name} not found.`)
        navigate('/baskets', { replace: true })
      }
    }

    loadBasketDetails();
  }, [name]);

  const refreshRequests = async (basketName: string) => {
    const basket = await BasketService.loadBasketDetails(basketName)
    setRequests(basket.requests)
  }

  const isLive = useBasketRefresh(name, refreshRequests)

  if (name === undefined) return null

  // Click-to-Copy:
  const url = basketUrl(name);
  const copy = (text: string, label: string) => {
    if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    setCopied(label);
    if (copyTimer.current) clearTimeout(copyTimer.current);
    copyTimer.current = setTimeout(() => setCopied(''), 1600);
  };

  const countLabel = `Requests: ${requests.length}`;

  // Styles
  const spotlightURLStyle = {
    fontSize: 15, padding: '10px 16px', borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg)', color: 'var(--color-accent-200)',
    boxShadow: 'inset 0 0 0 1px var(--color-accent-800)',
  }

  return (
    <main style={{ flex: 1, padding: '28px 28px 72px', maxWidth: 1080, width: '100%', margin: '0 auto' }}>
      {/* Basket Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
            <h4 style={{ margin: 0 }}>
              Basket: <span className="mono" style={{ color: 'var(--color-accent-300)' }}>{name}</span>
            </h4>
            <span className="tag tag-neutral mono">{countLabel}</span>
          </div>
          
          <div className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8, fontSize: 13 }}>
            <span>Requests are collected at</span>
            <span className="mono" style={{ color: 'var(--color-text)' }}>
              {url}
            </span>
            <SVGButton path={ICON_COPY} onClick={() => copy(url, 'Copied')} title="Copy collection URL" className="btn btn-ghost" size={15} style={{ padding: '2px 4px' }} />
            <span style={{ color: 'var(--color-accent)', fontSize: 11 }}>{copied}</span>
          </div>
        </div>

        {/* Basket Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          { isLive !== null &&
            <span
              className="mono"
              title={ isLive
                ? 'Receiving live updates'
                : 'Live updates stopped - reload the page to restart them' }
              style={{ display: 'flex', alignItems: 'center', gap: 5, marginRight: 4, fontSize: 12 }}
            >
              <span style={{
                width: 8, height: 8, borderRadius: '50%',
                background: isLive ? '#9ad99a' : '#d99a9a',
              }} />
              { isLive ? 'Live' : 'Disconnected' }
            </span>
          }
          <SVGButton path={ICON_LINK} onClick={() => copy(window.location.href, 'Link copied')} title="Copy share link" />
          <SVGButton path={ICON_TRASH} onClick={() => onDelete(name)} title="Delete basket" style={{ color: '#d99a9a' }} />
        </div>
      </div>

      <div className="hr" style={{ margin: '20px 0 4px' }} />

      {/* Requests List */}
      { requests.length > 0 && 
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 16 }}>
          { requests.map((req) => (
            <RequestCard key={req.id} request={req} />
          )) }
        </div>
      }

      {/* Empty Request List */}
      { requests.length === 0 && 
        <div className="card elev-sm" style={{ marginTop: 20, padding: '56px 28px', alignItems: 'center', textAlign: 'center', gap: 10 }}>
          <div className="text-muted" style={{ fontSize: 14 }}>
            No requests received yet.
          </div>
          <div className="mono" style={spotlightURLStyle}>{url}</div>
          <div className="text-muted" style={{ fontSize: 12, maxWidth: 380 }}>
            Send anything to that URL — every method, header and body is captured here.
          </div>
        </div>
      }
    </main>
  );
}

export default BasketPage;
