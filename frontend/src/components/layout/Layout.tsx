import type { ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
}

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/campaigns': 'Campaign Overview',
  '/viewability': 'Viewability & Health',
  '/segments': 'Audience Segments',
  '/anomalies': 'Anomaly Alerts',
  '/attribution': 'Attribution Modeling',
  '/ab-testing': 'A/B Testing',
  '/frequency': 'Frequency & Reach',
};

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const title = pageTitles[location.pathname] || 'Dashboard';

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
