'use client';

import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Plus, Shield, Globe } from 'lucide-react';

export interface ContextBreadcrumbItem {
  label: string;
  href?: string;
}

export interface ContextHeaderProps {
  breadcrumbs: ContextBreadcrumbItem[];
  privacyMode?: boolean;
  onPrivacyModeChange?: (enabled: boolean) => void;
  onNewMission?: () => void;
  className?: string;
}

/**
 * ContextHeader - Breadcrumbs and global actions (embedded in header)
 */
export function ContextHeader({
  breadcrumbs,
  privacyMode = false,
  onPrivacyModeChange,
  onNewMission,
  className,
}: ContextHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between flex-1', className)}>
      {/* Breadcrumbs */}
      <Breadcrumb>
        <BreadcrumbList>
          {breadcrumbs.map((item, index) => (
            <React.Fragment key={index}>
              <BreadcrumbItem className="hidden md:block">
                {item.href ? (
                  <BreadcrumbLink asChild>
                    <Link href={item.href}>{item.label}</Link>
                  </BreadcrumbLink>
                ) : (
                  <BreadcrumbPage>{item.label}</BreadcrumbPage>
                )}
              </BreadcrumbItem>
              {index < breadcrumbs.length - 1 && (
                <BreadcrumbSeparator className="hidden md:block" />
              )}
            </React.Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>

      {/* Actions */}
      <div className="flex items-center gap-3 ml-auto">
        {/* Privacy Mode Toggle */}
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center gap-2">
                <div
                  className={cn(
                    'flex items-center gap-1.5 text-xs font-medium',
                    privacyMode ? 'text-emerald-400' : 'text-muted-foreground'
                  )}
                >
                  {privacyMode ? (
                    <Shield className="size-3.5" />
                  ) : (
                    <Globe className="size-3.5" />
                  )}
                  <span className="hidden sm:inline">
                    {privacyMode ? 'Private' : 'Global'}
                  </span>
                </div>
                <Switch
                  checked={privacyMode}
                  onCheckedChange={onPrivacyModeChange}
                  className="data-[state=checked]:bg-emerald-600"
                />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xs">
                {privacyMode
                  ? 'Private Mode: Only your personal data moat is used'
                  : 'Global Mode: Access to shared knowledge base'}
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {/* New Mission Button */}
        {onNewMission && (
          <Button variant="outline" size="sm" onClick={onNewMission} className="gap-1.5">
            <Plus className="size-4" />
            <span className="hidden sm:inline">New</span>
          </Button>
        )}
      </div>
    </div>
  );
}
