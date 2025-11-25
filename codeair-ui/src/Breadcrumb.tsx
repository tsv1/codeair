import { type ReactNode } from 'react';
import { Link } from './Link';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: ReactNode;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="breadcrumb" aria-label="breadcrumbs">
      <ul>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={index} className={isLast ? 'is-active' : undefined}>
              {isLast || !item.href ? (
                <a href={item.href || '#'} aria-current={isLast ? 'page' : undefined}>
                  {false && item.icon && (<span className="icon is-small">{item.icon}</span>)}
                  <span>{item.label}</span>
                </a>
              ) : (
                <Link href={item.href}>
                  {index == 0 && item.icon && (<span className="icon is-small">{item.icon}</span>)}
                  <span>{item.label}</span>
                </Link>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
