import { useState, useEffect, useCallback } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import {
  Tv,
  LayoutDashboard,
  BarChart3,
  Eye,
  Users,
  AlertTriangle,
  GitBranch,
  FlaskConical,
  Radio,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useFilters } from '../../hooks/useFilters';
import {
  fetchOverview,
  fetchCampaigns,
  fetchViewability,
  fetchAnomalies,
  fetchAttribution,
  fetchFrequency,
} from '../../api/endpoints';

const STORAGE_KEY = 'ctv-sidebar-collapsed';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard, queryKey: 'overview' },
  { path: '/campaigns', label: 'Campaigns', icon: BarChart3, queryKey: 'campaigns' },
  { path: '/viewability', label: 'Viewability', icon: Eye, queryKey: 'viewability' },
  { path: '/segments', label: 'Segments', icon: Users, queryKey: 'segmentation' },
  { path: '/anomalies', label: 'Anomalies', icon: AlertTriangle, queryKey: 'anomalies' },
  { path: '/attribution', label: 'Attribution', icon: GitBranch, queryKey: 'attribution' },
  { path: '/ab-testing', label: 'A/B Testing', icon: FlaskConical, queryKey: 'ab-testing' },
  { path: '/frequency', label: 'Frequency', icon: Radio, queryKey: 'frequency' },
] as const;

// Map route queryKeys to their fetch functions
const prefetchMap: Record<string, (filters: any) => Promise<any>> = {
  overview: (f) => fetchOverview(f),
  campaigns: (f) => fetchCampaigns(f),
  viewability: (f) => fetchViewability(f),
  anomalies: (f) => fetchAnomalies(f),
  attribution: (f) => fetchAttribution(f),
  frequency: (f) => fetchFrequency(f),
};

export default function Sidebar() {
  const location = useLocation();
  const queryClient = useQueryClient();
  const { filters } = useFilters();
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(collapsed));
    } catch {
      // localStorage unavailable
    }
  }, [collapsed]);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  // Prefetch data on hover for faster page transitions
  const handlePrefetch = useCallback((queryKey: string) => {
    if (!filters.start_date) return;
    const fetchFn = prefetchMap[queryKey];
    if (fetchFn) {
      queryClient.prefetchQuery({
        queryKey: [queryKey, filters],
        queryFn: () => fetchFn(filters),
        staleTime: 5 * 60 * 1000,
      });
    }
  }, [queryClient, filters]);

  return (
    <aside
      className={`flex flex-col bg-slate-800 border-r border-slate-700 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-60'
      }`}
    >
      {/* Brand */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-700/50">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 shrink-0">
          <Tv className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-slate-100 whitespace-nowrap overflow-hidden">
            CTV Ad Intelligence
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
        {navItems.map(({ path, label, icon: Icon, queryKey }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            onMouseEnter={() => handlePrefetch(queryKey)}
            className={() =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive(path)
                  ? 'bg-slate-700/50 text-blue-400 border-l-2 border-blue-400 -ml-0.5 pl-[10px]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'
              }`
            }
            title={collapsed ? label : undefined}
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <div className="border-t border-slate-700/50 p-2">
        <button
          onClick={() => setCollapsed((prev) => !prev)}
          className="flex items-center justify-center w-full rounded-lg px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/30 transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5 mr-2" />
              <span className="text-sm">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
