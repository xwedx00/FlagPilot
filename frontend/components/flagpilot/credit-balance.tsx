'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Coins, TrendingUp, AlertTriangle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface CreditBalanceProps {
  current: number;
  total: number;
  className?: string;
  variant?: 'compact' | 'full';
  onTopUp?: () => void;
}

/**
 * CreditBalance - Displays credit meter with visual progress bar
 * 
 * Shows remaining credits with a 2px progress bar.
 * Clicking opens the top-up modal.
 * 
 * @example
 * <CreditBalance current={245} total={500} onTopUp={() => openModal()} />
 */
export function CreditBalance({
  current,
  total,
  className,
  variant = 'compact',
  onTopUp,
}: CreditBalanceProps) {
  const percentage = Math.min((current / total) * 100, 100);
  const isLow = percentage < 20;
  const isCritical = percentage < 10;

  if (variant === 'compact') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={onTopUp}
              className={cn(
                'w-full group cursor-pointer',
                'px-3 py-2 rounded-md',
                'hover:bg-zinc-800/50 transition-colors duration-75',
                className
              )}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <Coins className="w-3 h-3 text-purple-400" />
                  <span className="text-xs font-mono text-zinc-400">
                    Credits
                  </span>
                </div>
                <span
                  className={cn(
                    'text-xs font-mono font-semibold',
                    isCritical
                      ? 'text-rose-400'
                      : isLow
                      ? 'text-amber-400'
                      : 'text-zinc-300'
                  )}
                >
                  {current.toLocaleString()}
                </span>
              </div>

              {/* Progress bar */}
              <div className="fp-credit-bar">
                <div
                  className={cn(
                    'fp-credit-fill',
                    isCritical && 'from-rose-600 to-rose-400',
                    isLow && !isCritical && 'from-amber-600 to-amber-400'
                  )}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </button>
          </TooltipTrigger>
          <TooltipContent side="right" className="font-mono text-xs">
            <p>
              {current.toLocaleString()} / {total.toLocaleString()} credits
            </p>
            <p className="text-zinc-400">Click to top up</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Full variant with more details
  return (
    <div
      className={cn(
        'bg-zinc-900/60 backdrop-blur border border-zinc-700 rounded-md p-4',
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-purple-500/20 flex items-center justify-center">
            <Coins className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <p className="text-sm font-medium">Credit Balance</p>
            <p className="text-xs text-zinc-400">
              {Math.round(percentage)}% remaining
            </p>
          </div>
        </div>

        {isCritical && (
          <div className="flex items-center gap-1 text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs font-mono">Low</span>
          </div>
        )}
      </div>

      {/* Large balance display */}
      <div className="flex items-baseline gap-2 mb-3">
        <span
          className={cn(
            'text-3xl font-mono font-bold',
            isCritical
              ? 'text-rose-400'
              : isLow
              ? 'text-amber-400'
              : 'text-white'
          )}
        >
          {current.toLocaleString()}
        </span>
        <span className="text-sm text-zinc-500 font-mono">
          / {total.toLocaleString()}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden mb-3">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            isCritical
              ? 'bg-gradient-to-r from-rose-600 to-rose-400'
              : isLow
              ? 'bg-gradient-to-r from-amber-600 to-amber-400'
              : 'bg-gradient-to-r from-purple-600 to-purple-400'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Top up button */}
      {onTopUp && (
        <button
          onClick={onTopUp}
          className={cn(
            'w-full py-2 px-4 rounded-md text-sm font-medium',
            'bg-purple-600 hover:bg-purple-500 text-white',
            'transition-all duration-75 active:scale-[0.98]'
          )}
        >
          <TrendingUp className="w-4 h-4 inline mr-2" />
          Top Up Credits
        </button>
      )}
    </div>
  );
}

/**
 * Mini credit display for headers
 */
export function CreditBadge({
  current,
  className,
}: {
  current: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md',
        'bg-zinc-800/50 border border-zinc-700',
        className
      )}
    >
      <Coins className="w-3 h-3 text-purple-400" />
      <span className="text-xs font-mono font-semibold text-zinc-300">
        {current.toLocaleString()}
      </span>
    </div>
  );
}
