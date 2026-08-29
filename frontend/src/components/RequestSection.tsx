import type { ReactNode } from 'react';

interface RequestSectionProps {
  label: string;
  count: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
}

function RequestSection({ label, count, open, onToggle, children }: RequestSectionProps) {
  return (
    <div style={{ boxShadow: 'inset 0 1px 0 color-mix(in srgb, var(--color-text) 8%, transparent)' }}>
      <button
        className="rowbtn"
        onClick={onToggle}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          width: '100%',
          padding: '9px 14px',
          background: 'transparent',
          border: 0,
          cursor: 'pointer',
          color: 'var(--color-text)',
          font: 'inherit',
          fontSize: 13,
          textAlign: 'left',
        }}
      >
        <span className="text-muted mono" style={{ fontSize: 10, width: 9 }}>
          {open ? '▾' : '▸'}
        </span>
        <span>{label}</span>
        <span className="text-muted mono" style={{ fontSize: 11 }}>
          {count}
        </span>
      </button>
      {open && <div style={{ padding: '0 14px 14px 31px' }}>{children}</div>}
    </div>
  );
}

export default RequestSection;
