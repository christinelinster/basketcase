// >> React
import { useEffect, useRef, useState } from 'react';
// > Components
import RequestCard from './RequestCard';
// > Types
import type { CapturedRequest } from '../types/basket';

import { makeRequest, seedRequests } from '../lib/mockData';

const RECENT_LIMIT = 10;

interface BasketPageProps {
  name: string,
  onDelete: () => void;
}

function BasketPage({ name, onDelete }: BasketPageProps) {

  const [requests, setRequests] = useState<CapturedRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [auto, setAuto] = useState(false);
  const [copied, setCopied] = useState('');
  const seq = useRef(0);
  const timer = useRef<number | null>(null);
  const copyTimer = useRef<number | null>(null);

  if (name === undefined) return

  useEffect(() => {
    const seeds = seedRequests(name, RECENT_LIMIT);
    setRequests(seeds.list);
    setTotal(seeds.total);
    seq.current = 0;
    return () => {
      if (timer.current) window.clearInterval(timer.current);
      timer.current = null;
      setAuto(false);
    };
  }, [name]);

  const url = `https://basketcase.com/${name}`;

  const copy = (text: string, label: string) => {
    if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    setCopied(label);
    if (copyTimer.current) window.clearTimeout(copyTimer.current);
    copyTimer.current = window.setTimeout(() => setCopied(''), 1600);
  };

  const pushRequest = () => {
    seq.current += 1;
    const rand = Math.random;
    const req = makeRequest(rand, Date.now(), seq.current + 100);
    setRequests((r) => [req, ...r].slice(0, RECENT_LIMIT));
    setTotal((t) => t + 1);
  };

  const toggleAuto = () => {
    if (timer.current) {
      window.clearInterval(timer.current);
      timer.current = null;
      setAuto(false);
    } else {
      timer.current = window.setInterval(pushRequest, 2500);
      setAuto(true);
    }
  };

  const countLabel = `Requests: ${requests.length} (${total})`;
  const autoStyle = auto ? { color: 'var(--color-accent)', borderColor: 'var(--color-accent)' } : {};

  return (
    <main style={{ flex: 1, padding: '28px 28px 72px', maxWidth: 1080, width: '100%', margin: '0 auto' }}>
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
            <button className="btn btn-ghost" onClick={() => copy(url, 'Copied')} title="Copy collection URL" style={{ padding: '2px 4px' }}>
              <svg width="15" height="15" viewBox="0 0 256 256" fill="currentColor">
                <path d="M216 32H88a8 8 0 00-8 8v40H40a8 8 0 00-8 8v128a8 8 0 008 8h128a8 8 0 008-8v-40h40a8 8 0 008-8V40a8 8 0 00-8-8zm-56 176H48V96h112zm48-48h-32V88a8 8 0 00-8-8H96V48h112z" />
              </svg>
            </button>
            <span style={{ color: 'var(--color-accent)', fontSize: 11 }}>{copied}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button className="btn btn-secondary btn-icon" onClick={pushRequest} title="Refresh">
            <svg width="17" height="17" viewBox="0 0 256 256" fill="currentColor">
              <path d="M240 56v48a8 8 0 01-8 8h-48a8 8 0 010-16h28.69L182.06 73.37a79.56 79.56 0 00-56.13-23.37h-.45A79.52 79.52 0 0069.59 73a8 8 0 01-11.18-11.44 96 96 0 01135 .79L224 84.69V56a8 8 0 0116 0zm-53.59 126A80 80 0 0173.94 182.63L51.31 160H80a8 8 0 000-16H32a8 8 0 00-8 8v48a8 8 0 0016 0v-28.69l22.63 22.63A95.4 95.4 0 00128 222h.53a95.36 95.36 0 0069.06-28.55A8 8 0 00186.41 182z" />
            </svg>
          </button>
          <button className="btn btn-secondary btn-icon" onClick={toggleAuto} title="Toggle auto-refresh" style={autoStyle}>
            <svg width="17" height="17" viewBox="0 0 256 256" fill="currentColor">
              <path d="M128 40a96 96 0 1096 96 8 8 0 00-16 0 80 80 0 11-80-80 8 8 0 000-16zm8 88V72a8 8 0 00-16 0v56a8 8 0 004 6.93l40 23.09a8 8 0 008-13.86zm40-96h48a8 8 0 010 16h-48a8 8 0 010-16z" />
            </svg>
          </button>
          <button className="btn btn-secondary btn-icon" onClick={() => copy(window.location.href, 'Link copied')} title="Copy share link">
            <svg width="17" height="17" viewBox="0 0 256 256" fill="currentColor">
              <path d="M137.54 186.36a8 8 0 010 11.31l-9.94 9.94a56 56 0 01-79.2-79.2l24.12-24.12a56 56 0 0176.81-2.28 8 8 0 01-10.64 12 40 40 0 00-54.85 1.63L59.72 139.7a40 40 0 0056.57 56.57l9.93-9.94a8 8 0 0111.32.03zm70.06-138a56.06 56.06 0 00-79.2 0l-9.94 9.95a8 8 0 0011.32 11.31l9.94-9.93a40 40 0 0156.56 56.56l-24.12 24.12a40 40 0 01-54.85 1.6a8 8 0 00-10.63 12 56 56 0 0076.8-2.26l24.12-24.12a56.08 56.08 0 000-79.2z" />
            </svg>
          </button>
          <button className="btn btn-secondary btn-icon" onClick={onDelete} title="Delete basket" style={{ color: '#d99a9a' }}>
            <svg width="17" height="17" viewBox="0 0 256 256" fill="currentColor">
              <path d="M216 48h-40v-8a24 24 0 00-24-24h-48a24 24 0 00-24 24v8H40a8 8 0 000 16h8v144a16 16 0 0016 16h128a16 16 0 0016-16V64h8a8 8 0 000-16zM96 40a8 8 0 018-8h48a8 8 0 018 8v8H96zm96 168H64V64h128zm-80-104v64a8 8 0 01-16 0v-64a8 8 0 0116 0zm48 0v64a8 8 0 01-16 0v-64a8 8 0 0116 0z" />
            </svg>
          </button>
        </div>
      </div>

      <div className="hr" style={{ margin: '20px 0 4px' }} />

      {requests.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 16 }}>
          {requests.map((req) => (
            <RequestCard key={req.id} request={req} />
          ))}
        </div>
      ) : (
        <div className="card elev-sm" style={{ marginTop: 20, padding: '56px 28px', alignItems: 'center', textAlign: 'center', gap: 10 }}>
          <div className="text-muted" style={{ fontSize: 14 }}>
            No requests received yet.
          </div>
          <div
            className="mono"
            style={{
              fontSize: 15,
              padding: '10px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-bg)',
              color: 'var(--color-accent-200)',
              boxShadow: 'inset 0 0 0 1px var(--color-accent-800)',
            }}
          >
            {url}
          </div>
          <div className="text-muted" style={{ fontSize: 12, maxWidth: 380 }}>
            Send anything to that URL — every method, header and body is captured here.
          </div>
        </div>
      )}
    </main>
  );
}

export default BasketPage;
