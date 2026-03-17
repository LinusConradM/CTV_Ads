import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  text?: string;
}

export default function LoadingSpinner({ text = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
      <p className="mt-3 text-sm text-slate-400">{text}</p>
    </div>
  );
}
