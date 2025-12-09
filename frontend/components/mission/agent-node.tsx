"use client";

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { cn } from '@/lib/utils';
import { AGENTS, AGENT_SQUADS, type AgentId, type AgentStatus } from '@/stores/mission-store';
import { Badge } from '@/components/ui/badge';
import { Loader } from '@/components/ui/loader';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

export interface AgentNodeData {
  agentId: AgentId;
  status: AgentStatus;
  currentAction?: string;
  progress?: number;
  thought?: string;
}

interface AgentNodeProps {
  data: AgentNodeData;
  selected?: boolean;
}

const statusColors: Record<AgentStatus, string> = {
  idle: 'bg-slate-500',
  thinking: 'bg-yellow-500 animate-pulse',
  working: 'bg-blue-500 animate-pulse',
  waiting: 'bg-orange-500',
  done: 'bg-green-500',
  error: 'bg-red-500',
};

const statusLabels: Record<AgentStatus, string> = {
  idle: 'Idle',
  thinking: 'Thinking...',
  working: 'Working...',
  waiting: 'Waiting',
  done: 'Done',
  error: 'Error',
};

function AgentNodeComponent({ data, selected }: AgentNodeProps) {
  const agent = AGENTS[data.agentId];
  if (!agent) return null;
  
  const squad = AGENT_SQUADS[agent.squad as keyof typeof AGENT_SQUADS];
  const isActive = data.status === 'thinking' || data.status === 'working';
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              'relative rounded-xl border-2 bg-slate-900/95 backdrop-blur-sm p-3 min-w-[180px] transition-all duration-300',
              selected && 'ring-2 ring-primary ring-offset-2 ring-offset-slate-950',
              isActive && 'shadow-lg shadow-primary/20 scale-105',
              data.status === 'error' && 'border-red-500/50',
              data.status === 'done' && 'border-green-500/30',
              !isActive && data.status !== 'error' && data.status !== 'done' && 'border-slate-700/50'
            )}
            style={{
              borderColor: isActive ? squad.color : undefined,
            }}
          >
            {/* Connection handles */}
            <Handle
              type="target"
              position={Position.Left}
              className="!bg-slate-600 !border-slate-500 !w-3 !h-3"
            />
            <Handle
              type="source"
              position={Position.Right}
              className="!bg-slate-600 !border-slate-500 !w-3 !h-3"
            />
            
            {/* Status indicator dot */}
            <div className="absolute -top-1 -right-1">
              <span className={cn('flex h-3 w-3 rounded-full', statusColors[data.status])}>
                {isActive && (
                  <span className={cn('absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping', statusColors[data.status])} />
                )}
              </span>
            </div>
            
            {/* Agent content */}
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <div 
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-lg text-xl transition-transform',
                  isActive && 'animate-bounce'
                )}
                style={{ backgroundColor: `${squad.color}20` }}
              >
                {agent.icon}
              </div>
              
              {/* Info */}
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-sm text-white truncate">
                  {agent.name}
                </h4>
                <p className="text-[10px] text-slate-400 truncate">
                  {agent.role}
                </p>
                
                {/* Status / Action */}
                <div className="mt-1 flex items-center gap-1">
                  {isActive && <Loader variant="dots" size="sm" />}
                  <span className={cn(
                    'text-[10px] font-medium',
                    data.status === 'error' ? 'text-red-400' :
                    data.status === 'done' ? 'text-green-400' :
                    isActive ? 'text-blue-400' : 'text-slate-500'
                  )}>
                    {data.currentAction || statusLabels[data.status]}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Thought bubble */}
            {data.thought && isActive && (
              <div className="mt-2 px-2 py-1.5 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <p className="text-[10px] text-slate-300 italic line-clamp-2">
                  "{data.thought}"
                </p>
              </div>
            )}
            
            {/* Progress bar */}
            {data.progress !== undefined && data.progress > 0 && data.progress < 100 && (
              <div className="mt-2 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${data.progress}%` }}
                />
              </div>
            )}
            
            {/* Squad badge */}
            <Badge 
              variant="outline" 
              className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-[8px] px-1.5 py-0 h-4 bg-slate-900 border-slate-700"
              style={{ color: squad.color }}
            >
              {squad.name.split(' ')[0]}
            </Badge>
          </div>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-[250px]">
          <div className="space-y-1">
            <p className="font-semibold">{agent.name}</p>
            <p className="text-xs text-muted-foreground">{agent.description}</p>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export const AgentNode = memo(AgentNodeComponent);
