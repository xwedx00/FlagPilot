'use client';

import * as React from 'react';
import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';

interface LogEntry {
  id: string;
  timestamp?: Date;
  type?: 'info' | 'success' | 'error' | 'warning' | 'system';
  message: string;
  agent?: string;
}

interface StreamableLogProps {
  logs: LogEntry[];
  className?: string;
  autoScroll?: boolean;
  showTimestamps?: boolean;
  maxHeight?: string;
}

const TYPE_COLORS: Record<string, string> = {
  info: 'text-zinc-400',
  success: 'text-emerald-400',
  error: 'text-rose-400',
  warning: 'text-amber-400',
  system: 'text-purple-400',
};

const TYPE_PREFIXES: Record<string, string> = {
  info: 'INFO',
  success: '✓ OK',
  error: '✗ ERR',
  warning: 'WARN',
  system: 'SYS',
};

/**
 * StreamableLog - Terminal-style log viewer with auto-scroll
 * 
 * Displays real-time logs from agents in a console aesthetic.
 * Uses bg-black, text-green-400 for the classic terminal look.
 * 
 * @example
 * <StreamableLog 
 *   logs={[
 *     { id: '1', message: 'Analyzing contract...', type: 'info' },
 *     { id: '2', message: 'Found 3 risk clauses', type: 'warning' },
 *   ]} 
 * />
 */
export function StreamableLog({
  logs,
  className,
  autoScroll = true,
  showTimestamps = true,
  maxHeight = '300px',
}: StreamableLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const formatTimestamp = (date?: Date): string => {
    if (!date) return '';
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div
      className={cn(
        'bg-black rounded-sm border border-zinc-800 overflow-hidden',
        className
      )}
      style={{ maxHeight }}
    >
      <ScrollArea className="h-full">
        <div
          ref={scrollRef}
          className="p-3 font-mono text-xs leading-relaxed space-y-0.5"
        >
          {logs.length === 0 ? (
            <div className="text-zinc-600 italic">
              {'>'} Waiting for agent output...
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className={cn(
                  'flex gap-2 fp-terminal-line',
                  TYPE_COLORS[log.type || 'info']
                )}
              >
                {/* Prompt character */}
                <span className="text-zinc-600 select-none">{'>'}</span>

                {/* Timestamp */}
                {showTimestamps && log.timestamp && (
                  <span className="text-zinc-600 tabular-nums">
                    [{formatTimestamp(log.timestamp)}]
                  </span>
                )}

                {/* Type prefix */}
                {log.type && (
                  <span
                    className={cn(
                      'font-semibold min-w-[4ch]',
                      TYPE_COLORS[log.type]
                    )}
                  >
                    {TYPE_PREFIXES[log.type]}
                  </span>
                )}

                {/* Agent name */}
                {log.agent && (
                  <span className="text-purple-400 font-semibold">
                    [{log.agent}]
                  </span>
                )}

                {/* Message */}
                <span className="text-green-400 flex-1 break-all">
                  {log.message}
                </span>
              </div>
            ))
          )}
          <div ref={endRef} />
        </div>
      </ScrollArea>
    </div>
  );
}

/**
 * Hook to manage streaming logs
 */
export function useStreamingLogs(maxLogs: number = 500) {
  const [logs, setLogs] = React.useState<LogEntry[]>([]);
  const idCounter = useRef(0);

  const addLog = React.useCallback(
    (
      message: string,
      options?: {
        type?: LogEntry['type'];
        agent?: string;
      }
    ) => {
      const newLog: LogEntry = {
        id: `log-${idCounter.current++}`,
        timestamp: new Date(),
        message,
        type: options?.type || 'info',
        agent: options?.agent,
      };

      setLogs((prev) => {
        const updated = [...prev, newLog];
        // Keep only the last maxLogs entries
        return updated.slice(-maxLogs);
      });
    },
    [maxLogs]
  );

  const clearLogs = React.useCallback(() => {
    setLogs([]);
  }, []);

  return { logs, addLog, clearLogs };
}

export type { LogEntry };
