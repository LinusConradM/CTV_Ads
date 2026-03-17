import { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

interface Column {
  key: string;
  label: string;
  format?: (value: any) => string;
}

interface DataTableProps {
  columns: Column[];
  data: Record<string, any>[];
  pageSize?: number;
}

type SortDir = 'asc' | 'desc' | null;

export default function DataTable({
  columns,
  data,
  pageSize = 10,
}: DataTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);
  const [page, setPage] = useState(0);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDir === 'asc') setSortDir('desc');
      else if (sortDir === 'desc') {
        setSortKey(null);
        setSortDir(null);
      }
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
    setPage(0);
  };

  const sorted = useMemo(() => {
    if (!sortKey || !sortDir) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const pageData = sorted.slice(page * pageSize, (page + 1) * pageSize);

  const SortIcon = ({ colKey }: { colKey: string }) => {
    if (sortKey !== colKey)
      return <ChevronsUpDown className="w-3.5 h-3.5 text-slate-500" />;
    return sortDir === 'asc' ? (
      <ChevronUp className="w-3.5 h-3.5 text-blue-400" />
    ) : (
      <ChevronDown className="w-3.5 h-3.5 text-blue-400" />
    );
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-slate-200 select-none"
                >
                  <span className="inline-flex items-center gap-1.5">
                    {col.label}
                    <SortIcon colKey={col.key} />
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {pageData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-8 text-center text-slate-500"
                >
                  No data available
                </td>
              </tr>
            ) : (
              pageData.map((row, idx) => (
                <tr
                  key={idx}
                  className={`transition-colors hover:bg-slate-700/20 ${
                    idx % 2 === 1 ? 'bg-slate-800/30' : ''
                  }`}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className="px-4 py-3 text-slate-300 whitespace-nowrap"
                    >
                      {col.format ? col.format(row[col.key]) : String(row[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {sorted.length > pageSize && (
        <div className="flex items-center justify-between border-t border-slate-700/50 px-4 py-3">
          <span className="text-xs text-slate-500">
            Showing {page * pageSize + 1}&ndash;
            {Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-700/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  i === page
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'
                }`}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 rounded text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-700/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
