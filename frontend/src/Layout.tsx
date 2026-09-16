import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return <div className="mx-auto flex min-h-screen max-w-md flex-col">{children}</div>;
}
