import type { ReactNode, MouseEvent, AnchorHTMLAttributes } from 'react';

interface LinkProps extends Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'onClick'> {
  href: string;
  children: ReactNode;
  onClick?: (e: MouseEvent<HTMLAnchorElement>) => void;
}

/**
 * A link component that supports Cmd/Ctrl+click to open in new tab
 * while maintaining SPA navigation for regular clicks
 */
export function Link({ href, children, onClick, ...props }: LinkProps) {
  const handleClick = (e: MouseEvent<HTMLAnchorElement>) => {
    // Allow cmd/ctrl+click to open in new tab
    if (e.metaKey || e.ctrlKey) return;

    e.preventDefault();

    // Call custom onClick handler if provided
    if (onClick) {
      onClick(e);
    }

    // Navigate using window.location for SPA behavior
    window.location.href = href;
  };

  return (
    <a href={href} onClick={handleClick} {...props}>
      {children}
    </a>
  );
}
