'use client';

import * as React from 'react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import { CommandSidebar, type Mission, type Agent } from './command-sidebar';
import { ContextHeader, type ContextBreadcrumbItem } from './context-header';
import { BillingModal } from './billing-modal';

interface AppLayoutProps {
  children: React.ReactNode;
  breadcrumbs?: ContextBreadcrumbItem[];
  user?: {
    name: string;
    email: string;
    avatarUrl?: string;
  };
  missions?: Mission[];
  agents?: Agent[];
  credits?: {
    current: number;
    total: number;
  };
  showHeader?: boolean;
  className?: string;
}

/**
 * AppLayout - Main application shell with sidebar and header
 * 
 * Uses shadcn/ui SidebarProvider for collapsible sidebar functionality.
 */
export function AppLayout({
  children,
  breadcrumbs = [{ label: 'Home', href: '/' }],
  user = { name: 'User', email: 'user@example.com' },
  missions = [],
  agents,
  credits = { current: 245, total: 500 },
  showHeader = true,
  className,
}: AppLayoutProps) {
  const [showBillingModal, setShowBillingModal] = useState(false);
  const [privacyMode, setPrivacyMode] = useState(false);

  const handleNewMission = () => {
    console.log('New mission');
  };

  const handleTopUpCredits = () => {
    setShowBillingModal(true);
  };

  const handleLogout = () => {
    console.log('Logout');
  };

  const handleSelectPlan = async (planId: string) => {
    console.log('Selected plan:', planId);
    await new Promise((r) => setTimeout(r, 2000));
  };

  const handleBuyCredits = async (creditsAmount: number) => {
    console.log('Buying credits:', creditsAmount);
    await new Promise((r) => setTimeout(r, 2000));
  };

  return (
    <SidebarProvider>
      <CommandSidebar
        user={user}
        missions={missions}
        agents={agents}
        credits={credits}
        onNewMission={handleNewMission}
        onTopUpCredits={handleTopUpCredits}
        onLogout={handleLogout}
      />

      <SidebarInset className={cn('flex flex-col', className)}>
        {/* Header */}
        {showHeader && (
          <header className="flex h-14 shrink-0 items-center border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center gap-3 px-5 w-full">
              <SidebarTrigger className="size-8" />
              <Separator orientation="vertical" className="h-5" />
              <ContextHeader
                breadcrumbs={breadcrumbs}
                privacyMode={privacyMode}
                onPrivacyModeChange={setPrivacyMode}
                onNewMission={handleNewMission}
              />
            </div>
          </header>
        )}

        {/* Content */}
        <main className="flex-1 overflow-hidden">{children}</main>
      </SidebarInset>

      {/* Billing modal */}
      <BillingModal
        open={showBillingModal}
        onOpenChange={setShowBillingModal}
        currentCredits={credits.current}
        onSelectPlan={handleSelectPlan}
        onBuyCredits={handleBuyCredits}
      />
    </SidebarProvider>
  );
}

export type { AppLayoutProps };
