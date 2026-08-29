import { Fragment, useState } from 'react';
import type { CapturedRequest } from '../types/basket';
import { ago, fmtTime } from '../lib/mockData';
import RequestSection from './RequestSection';

interface RequestCardProps {
  request: CapturedRequest;
}

function RequestCard({ request }: RequestCardProps) {
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [pretty, setPretty] = useState(false);

  const toggle = (key: string) => setOpen((o) => ({ ...o, [key]: !o[key] }));

  const query = request.query
    ? request.query.split('&').map((p) => ({ k: p.split('=')[0], v: p.split('=').slice(1).join('=') }))
    : [];

  let bodyText = request.body || '— empty —';
  if (pretty && request.body) {
    try {
      bodyText = JSON.stringify(JSON.parse(request.body), null, 2);
    } catch {
      bodyText = request.body.split('&').join('\n&');
    }
  }

  const path = request.query ? `${request.path}?${request.query}` : request.path;

  return (
    <article className="card elev-sm" style={{ padding: 0, gap: 0, overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px' }}>
        <span
          className="mono"
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: '0.06em',
            padding: '3px 8px',
            borderRadius: 4,
            color: request.fg,
            background: request.bg,
          }}
        >
          {request.method}
        </span>
        <span className="mono text-muted" style={{ fontSize: 12 }}>
          {fmtTime(request.ts)}
        </span>
        <span className="text-muted" style={{ fontSize: 11, marginLeft: 'auto' }}>
          {ago(request.ts)}
        </span>
      </div>
      <div
        className="mono"
        style={{
          margin: '0 14px 12px',
          padding: '9px 12px',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--color-bg)',
          fontSize: 13,
          color: 'var(--color-accent-200)',
          overflowX: 'auto',
          whiteSpace: 'nowrap',
        }}
      >
        {path}
      </div>

      <RequestSection label="Headers" count={String(request.headers.length)} open={!!open.headers} onToggle={() => toggle('headers')}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(120px,220px) minmax(0,1fr)', gap: '2px 16px' }}>
          {request.headers.map(([k, v], i) => (
            <Fragment key={i}>
              <div className="mono text-muted" style={{ fontSize: 12, padding: '3px 0' }}>
                {k}
              </div>
              <div className="mono" style={{ fontSize: 12, padding: '3px 0', wordBreak: 'break-all' }}>
                {v}
              </div>
            </Fragment>
          ))}
        </div>
      </RequestSection>

      <RequestSection label="Query Params" count={String(query.length)} open={!!open.query} onToggle={() => toggle('query')}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(120px,220px) minmax(0,1fr)', gap: '2px 16px' }}>
          {query.map((row, i) => (
            <Fragment key={i}>
              <div className="mono text-muted" style={{ fontSize: 12, padding: '3px 0' }}>
                {row.k}
              </div>
              <div className="mono" style={{ fontSize: 12, padding: '3px 0', wordBreak: 'break-all' }}>
                {row.v}
              </div>
            </Fragment>
          ))}
        </div>
      </RequestSection>

      <RequestSection
        label="Body"
        count={request.body ? `${request.body.length} B` : '0 B'}
        open={!!open.body}
        onToggle={() => toggle('body')}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <button className="btn btn-secondary" onClick={() => setPretty((p) => !p)} style={{ fontSize: 12, padding: '4px 10px' }}>
              {pretty ? 'Raw Content' : 'Format Content'}
            </button>
            <span className="text-muted mono" style={{ fontSize: 11 }}>
              {request.contentType}
            </span>
          </div>
          <pre
            className="mono"
            style={{
              margin: 0,
              padding: '11px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--color-bg)',
              fontSize: 12,
              lineHeight: 1.6,
              color: 'var(--color-neutral-200)',
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {bodyText}
          </pre>
        </div>
      </RequestSection>
    </article>
  );
}

export default RequestCard;
