'use client';

import * as React from 'react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Check, Loader2, Zap, Sparkles, Building2 } from 'lucide-react';

interface PricingTier {
  id: string;
  name: string;
  price: number;
  credits: number;
  features: string[];
  popular?: boolean;
  icon: React.ReactNode;
}

const PRICING_TIERS: PricingTier[] = [
  {
    id: 'hobby',
    name: 'Hobby',
    price: 9,
    credits: 500,
    features: [
      '500 credits/month',
      'All 13 agents',
      '5GB Personal Moat',
      'Email support',
    ],
    icon: <Zap className="w-5 h-5" />,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 29,
    credits: 2000,
    features: [
      '2,000 credits/month',
      'All 13 agents',
      '25GB Personal Moat',
      'Priority support',
      'API access',
      'Workflow templates',
    ],
    popular: true,
    icon: <Sparkles className="w-5 h-5" />,
  },
  {
    id: 'agency',
    name: 'Agency',
    price: 99,
    credits: 10000,
    features: [
      '10,000 credits/month',
      'All 13 agents',
      '100GB Personal Moat',
      'Dedicated support',
      'API access',
      'Custom workflows',
      'Team collaboration',
      'White-label reports',
    ],
    icon: <Building2 className="w-5 h-5" />,
  },
];

const CREDIT_PACKS = [
  { credits: 100, price: 5 },
  { credits: 250, price: 10 },
  { credits: 500, price: 18 },
  { credits: 1000, price: 30 },
];

interface BillingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentCredits?: number;
  onSelectPlan?: (planId: string) => Promise<void>;
  onBuyCredits?: (credits: number) => Promise<void>;
}

/**
 * PricingCard - Individual tier card with improved spacing
 */
function PricingCard({
  tier,
  onSelect,
  isLoading,
}: {
  tier: PricingTier;
  onSelect: () => void;
  isLoading?: boolean;
}) {
  return (
    <div
      className={cn(
        'relative rounded-lg p-5 border flex flex-col',
        tier.popular
          ? 'border-purple-500 bg-purple-500/5 ring-1 ring-purple-500/20'
          : 'border-zinc-700/50 bg-zinc-900/30'
      )}
    >
      {tier.popular && (
        <Badge className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs px-3">
          Most Popular
        </Badge>
      )}

      <div className="flex items-center gap-3 mb-4 pt-1">
        <div
          className={cn(
            'size-10 rounded-lg flex items-center justify-center',
            tier.popular ? 'bg-purple-500/20 text-purple-400' : 'bg-zinc-800 text-zinc-400'
          )}
        >
          {tier.icon}
        </div>
        <h3 className="font-semibold text-lg">{tier.name}</h3>
      </div>

      <div className="mb-2">
        <span className="text-4xl font-bold">${tier.price}</span>
        <span className="text-zinc-500 text-sm ml-1">/month</span>
      </div>

      <p className="text-sm text-zinc-400 mb-5 pb-4 border-b border-zinc-800">
        {tier.credits.toLocaleString()} credits included
      </p>

      <ul className="space-y-2.5 mb-6 flex-1">
        {tier.features.slice(0, 5).map((feature, index) => (
          <li key={index} className="flex items-start gap-2.5 text-sm">
            <Check className="size-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span className="text-zinc-300">{feature}</span>
          </li>
        ))}
        {tier.features.length > 5 && (
          <li className="text-xs text-zinc-500 pl-6">
            +{tier.features.length - 5} more features
          </li>
        )}
      </ul>

      <Button
        onClick={onSelect}
        disabled={isLoading}
        size="lg"
        className={cn(
          'w-full',
          tier.popular
            ? 'bg-purple-600 hover:bg-purple-500'
            : 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700'
        )}
      >
        {isLoading ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          `Choose ${tier.name}`
        )}
      </Button>
    </div>
  );
}

/**
 * BillingModal - Credit top-up and subscription modal
 * 
 * Features:
 * - Three tier pricing cards (Hobby, Pro, Agency)
 * - Pay-as-you-go credit slider
 * - Spinner while waiting for webhook confirmation
 */
export function BillingModal({
  open,
  onOpenChange,
  currentCredits = 0,
  onSelectPlan,
  onBuyCredits,
}: BillingModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [selectedCredits, setSelectedCredits] = useState(250);
  const [mode, setMode] = useState<'plans' | 'credits'>('plans');

  const selectedPack = CREDIT_PACKS.find((p) => p.credits === selectedCredits) || CREDIT_PACKS[1];

  const handleSelectPlan = async (planId: string) => {
    if (!onSelectPlan) return;
    setLoadingPlan(planId);
    try {
      await onSelectPlan(planId);
    } finally {
      setLoadingPlan(null);
    }
  };

  const handleBuyCredits = async () => {
    if (!onBuyCredits) return;
    setIsLoading(true);
    try {
      await onBuyCredits(selectedCredits);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl bg-zinc-950 border-zinc-800 p-0 gap-0 overflow-hidden">
        <DialogHeader className="p-6 pb-4 border-b border-zinc-800/50">
          <DialogTitle className="text-xl font-semibold">Top Up Credits</DialogTitle>
          <DialogDescription className="text-zinc-400">
            Current balance:{' '}
            <span className="text-purple-400 font-mono font-semibold">
              {currentCredits.toLocaleString()} credits
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="p-6 space-y-6">
          {/* Mode tabs */}
          <div className="flex gap-2">
            <Button
              variant={mode === 'plans' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setMode('plans')}
              className={cn(
                'px-4',
                mode === 'plans' ? 'bg-purple-600 hover:bg-purple-500' : 'border-zinc-700'
              )}
            >
              Subscription Plans
            </Button>
            <Button
              variant={mode === 'credits' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setMode('credits')}
              className={cn(
                'px-4',
                mode === 'credits' ? 'bg-purple-600 hover:bg-purple-500' : 'border-zinc-700'
              )}
            >
              Pay as You Go
            </Button>
          </div>

          {mode === 'plans' ? (
            /* Pricing tiers */
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {PRICING_TIERS.map((tier) => (
                <PricingCard
                  key={tier.id}
                  tier={tier}
                  onSelect={() => handleSelectPlan(tier.id)}
                  isLoading={loadingPlan === tier.id}
                />
              ))}
            </div>
          ) : (
          /* Pay as you go slider */
          <div className="space-y-6">
            <div className="bg-zinc-900/60 backdrop-blur border border-zinc-700 rounded-md p-6">
              <h4 className="text-sm font-medium mb-4">Select credit amount</h4>

              <Slider
                value={[selectedCredits]}
                onValueChange={(v: number[]) => setSelectedCredits(v[0])}
                min={100}
                max={1000}
                step={50}
                className="mb-4"
              />

              <div className="flex items-center justify-between">
                <div>
                  <span className="text-3xl font-bold font-mono">
                    {selectedCredits.toLocaleString()}
                  </span>
                  <span className="text-zinc-500 ml-2">credits</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold">${selectedPack.price}</span>
                  <p className="text-xs text-zinc-500">
                    ${(selectedPack.price / selectedPack.credits * 100).toFixed(1)}¢ per credit
                  </p>
                </div>
              </div>
            </div>

            <Button
              onClick={handleBuyCredits}
              disabled={isLoading}
              className="w-full bg-purple-600 hover:bg-purple-500 active:scale-[0.98] transition-transform h-12"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  Buy {selectedCredits.toLocaleString()} Credits for ${selectedPack.price}
                </>
              )}
            </Button>

            <p className="text-xs text-zinc-500 text-center">
              Payments processed securely via Polar.sh
            </p>
          </div>
        )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

export type { BillingModalProps, PricingTier };
