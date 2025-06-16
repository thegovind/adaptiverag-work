import { ReactNode } from 'react';
import { Card } from './ui/card';

interface ChatLayoutProps {
  children: ReactNode;
}

export function ChatLayout({ children }: ChatLayoutProps) {
  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
      <div className="flex-1 flex flex-col max-w-7xl mx-auto w-full px-6 py-6">
        <Card className="flex-1 flex flex-col shadow-lg border-0 bg-white/80 backdrop-blur-sm h-full">
          {children}
        </Card>
      </div>
    </div>
  );
}
