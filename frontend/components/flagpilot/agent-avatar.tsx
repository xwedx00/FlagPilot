'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import {
  Scale,
  Eye,
  Shield,
  FileSearch,
  Gavel,
  Search,
  Swords,
  Receipt,
  Coins,
  GraduationCap,
  MessageSquare,
  FolderLock,
  Bot,
  Zap,
} from 'lucide-react';

/**
 * All 13 FlagPilot agents with their icons
 * 
 * Orchestrator Squad: FlagPilot, Scribe, Connector, Vault Keeper
 * Risk & Legal Squad: Legal Eagle, Sentinel, Adjudicator, Job Authenticator
 * Growth & Finance Squad: Iris, Negotiator, Ledger, Payment Enforcer, Scope Sentinel
 */
const AGENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  // Orchestrator Squad
  'flagpilot': Zap,
  'orchestrator': Zap,
  'scribe': Bot,
  'project-manager': Bot,
  'connector': MessageSquare,
  'communications': MessageSquare,
  'vault-keeper': FolderLock,
  'file-manager': FolderLock,
  // Risk & Legal Squad
  'legal-eagle': Scale,
  'contract-guardian': Scale,
  'sentinel': Eye,
  'privacy-officer': Eye,
  'adjudicator': Gavel,
  'dispute-mediator': Gavel,
  'job-authenticator': FileSearch,
  // Growth & Finance Squad
  'iris': Search,
  'deep-research': Search,
  'negotiator': Swords,
  'ledger': Receipt,
  'finance-controller': Receipt,
  'payment-enforcer': Coins,
  'scope-sentinel': Shield,
  'coach': GraduationCap,
  'talent-mentor': GraduationCap,
};

/**
 * Agent color mapping for avatar backgrounds
 */
const AGENT_COLORS: Record<string, string> = {
  // Orchestrator Squad - Purple/Violet tones
  'flagpilot': 'bg-purple-500',
  'orchestrator': 'bg-purple-500',
  'scribe': 'bg-teal-600',
  'project-manager': 'bg-teal-600',
  'connector': 'bg-violet-600',
  'communications': 'bg-violet-600',
  'vault-keeper': 'bg-slate-600',
  'file-manager': 'bg-slate-600',
  // Risk & Legal Squad - Blue/Cyan tones
  'legal-eagle': 'bg-blue-600',
  'contract-guardian': 'bg-blue-600',
  'sentinel': 'bg-cyan-600',
  'privacy-officer': 'bg-cyan-600',
  'adjudicator': 'bg-rose-600',
  'dispute-mediator': 'bg-rose-600',
  'job-authenticator': 'bg-amber-600',
  // Growth & Finance Squad - Green/Orange tones
  'iris': 'bg-indigo-600',
  'deep-research': 'bg-indigo-600',
  'negotiator': 'bg-orange-600',
  'ledger': 'bg-green-600',
  'finance-controller': 'bg-green-600',
  'payment-enforcer': 'bg-emerald-600',
  'scope-sentinel': 'bg-fuchsia-600',
  'coach': 'bg-pink-600',
  'talent-mentor': 'bg-pink-600',
};

export type AgentStatus = 'idle' | 'working' | 'thinking' | 'error' | 'complete';

interface AgentAvatarProps {
  agentId: string;
  status?: AgentStatus;
  size?: 'sm' | 'md' | 'lg';
  showStatus?: boolean;
  className?: string;
}

const STATUS_CLASSES: Record<AgentStatus, string> = {
  idle: 'fp-status-idle',
  working: 'fp-status-working',
  thinking: 'fp-status-thinking',
  error: 'fp-status-error',
  complete: 'fp-status-complete',
};

const SIZE_CLASSES = {
  sm: 'w-6 h-6',
  md: 'w-8 h-8',
  lg: 'w-10 h-10',
};

const ICON_SIZE_CLASSES = {
  sm: 'w-3 h-3',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
};

const STATUS_SIZE_CLASSES = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
  lg: 'w-2.5 h-2.5',
};

/**
 * AgentAvatar - Circular avatar with agent-specific icon and status indicator
 * 
 * @example
 * <AgentAvatar agentId="contract-guardian" status="working" />
 * <AgentAvatar agentId="iris" size="lg" showStatus={false} />
 */
export function AgentAvatar({
  agentId,
  status = 'idle',
  size = 'md',
  showStatus = true,
  className,
}: AgentAvatarProps) {
  const normalizedId = agentId.toLowerCase().replace(/\s+/g, '-');
  const Icon = AGENT_ICONS[normalizedId] || Bot;
  const bgColor = AGENT_COLORS[normalizedId] || 'bg-zinc-600';

  return (
    <div className={cn('relative inline-flex', className)}>
      {/* Avatar circle */}
      <div
        className={cn(
          'rounded-md flex items-center justify-center',
          bgColor,
          SIZE_CLASSES[size]
        )}
      >
        <Icon className={cn('text-white', ICON_SIZE_CLASSES[size])} />
      </div>

      {/* Status indicator dot */}
      {showStatus && (
        <span
          className={cn(
            'absolute -bottom-0.5 -right-0.5 rounded-full ring-2 ring-zinc-950',
            STATUS_CLASSES[status],
            STATUS_SIZE_CLASSES[size]
          )}
        />
      )}
    </div>
  );
}

/**
 * Get the display name for an agent
 */
export function getAgentDisplayName(agentId: string): string {
  const names: Record<string, string> = {
    // Orchestrator Squad
    'flagpilot': 'FlagPilot',
    'orchestrator': 'FlagPilot',
    'scribe': 'Scribe',
    'project-manager': 'Scribe',
    'connector': 'Connector',
    'communications': 'Connector',
    'vault-keeper': 'Vault Keeper',
    'file-manager': 'Vault Keeper',
    // Risk & Legal Squad
    'legal-eagle': 'Legal Eagle',
    'contract-guardian': 'Legal Eagle',
    'sentinel': 'Sentinel',
    'privacy-officer': 'Sentinel',
    'adjudicator': 'Adjudicator',
    'dispute-mediator': 'Adjudicator',
    'job-authenticator': 'Job Auth',
    // Growth & Finance Squad
    'iris': 'Iris',
    'deep-research': 'Iris',
    'negotiator': 'Negotiator',
    'ledger': 'Ledger',
    'finance-controller': 'Ledger',
    'payment-enforcer': 'Enforcer',
    'scope-sentinel': 'Scope Guard',
    'coach': 'Coach',
    'talent-mentor': 'Coach',
  };
  
  return names[agentId.toLowerCase().replace(/\s+/g, '-')] || agentId;
}

export { AGENT_ICONS, AGENT_COLORS };
