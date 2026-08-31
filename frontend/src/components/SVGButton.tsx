import type { CSSProperties } from 'react';

interface SVGButtonProps {
  path: string;
  onClick: () => void;
  title: string;
  size?: number;
  className?: string;
  style?: CSSProperties;
}

function SVGButton({ path, onClick, title, size = 17, className = 'btn btn-secondary btn-icon', style }: SVGButtonProps) {
  return (
    <button className={className} onClick={onClick} title={title} style={style}>
      <svg width={size} height={size} viewBox="0 0 256 256" fill="currentColor">
        <path d={path} />
      </svg>
    </button>
  );
}

export default SVGButton;
