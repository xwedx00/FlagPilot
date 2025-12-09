'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from '@/components/ui/sidebar';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Progress } from '@/components/ui/progress';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  ChevronsUpDown,
  Zap,
  Folder,
  FolderLock,
  Settings,
  CreditCard,
  LogOut,
  Plus,
  Sparkles,
} from 'lucide-react';

export interface Mission {
  id: string;
  name: string;
  status: 'active' | 'completed' | 'paused';
  createdAt: Date;
}

export interface CommandSidebarProps {
  user: {
    name: string;
    email: string;
    avatarUrl?: string;
  };
  missions?: Mission[];
  credits: {
    current: number;
    total: number;
  };
  onNewMission?: () => void;
  onTopUpCredits?: () => void;
  onLogout?: () => void;
}

/**
 * NavUser - User profile dropdown in sidebar footer
 */
function NavUser({
  user,
  onTopUpCredits,
  onLogout,
}: {
  user: { name: string; email: string; avatarUrl?: string };
  onTopUpCredits?: () => void;
  onLogout?: () => void;
}) {
  const { isMobile } = useSidebar();

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarImage src={user.avatarUrl} alt={user.name} />
                <AvatarFallback className="rounded-lg bg-primary/20 text-primary">
                  {user.name.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground">{user.email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
            side={isMobile ? 'bottom' : 'right'}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarImage src={user.avatarUrl} alt={user.name} />
                  <AvatarFallback className="rounded-lg">{user.name.slice(0, 2)}</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">{user.name}</span>
                  <span className="truncate text-xs">{user.email}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={onTopUpCredits}>
                <Sparkles className="mr-2 h-4 w-4" />
                Upgrade to Pro
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem asChild>
                <Link href="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onTopUpCredits}>
                <CreditCard className="mr-2 h-4 w-4" />
                Billing
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={onLogout} className="text-destructive focus:text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

/**
 * CreditMeter - Shows credit balance in sidebar
 */
function CreditMeter({ current, total, onTopUp }: { current: number; total: number; onTopUp?: () => void }) {
  const percentage = Math.min((current / total) * 100, 100);
  const isLow = percentage < 20;

  return (
    <div className="p-3 border-t border-sidebar-border">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-muted-foreground">Credits</span>
        <button
          onClick={onTopUp}
          className="text-xs text-primary hover:text-primary/80 font-medium transition-colors"
        >
          Top up
        </button>
      </div>
      <div className="flex items-center gap-2">
        <Progress value={percentage} className={cn('h-1.5 flex-1', isLow && '[&>div]:bg-destructive')} />
        <span className={cn('text-xs font-mono tabular-nums', isLow ? 'text-destructive' : 'text-muted-foreground')}>
          {current.toLocaleString()}
        </span>
      </div>
    </div>
  );
}

/**
 * CommandSidebar - The main navigation sidebar using shadcn/ui Sidebar
 * Note: Agents section has been removed as per user request
 */
export function CommandSidebar({
  user,
  missions = [],
  credits,
  onNewMission,
  onTopUpCredits,
  onLogout,
  ...props
}: CommandSidebarProps & React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();

  return (
    <Sidebar collapsible="icon" {...props}>
      {/* Header with Logo */}
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Zap className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">FlagPilot</span>
                  <span className="truncate text-xs text-muted-foreground">Agency OS</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {/* New Mission Button */}
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={onNewMission}
                tooltip="New Mission"
                className="bg-primary/10 hover:bg-primary/20 text-primary"
              >
                <Plus className="size-4" />
                <span>New Mission</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>



        {/* Vault */}
        <SidebarGroup>
          <SidebarGroupLabel>Data Moat</SidebarGroupLabel>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname === '/vault'} tooltip="The Vault">
                <Link href="/vault">
                  <FolderLock className="size-4" />
                  <span>The Vault</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <CreditMeter current={credits.current} total={credits.total} onTopUp={onTopUpCredits} />
        <NavUser user={user} onTopUpCredits={onTopUpCredits} onLogout={onLogout} />
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
