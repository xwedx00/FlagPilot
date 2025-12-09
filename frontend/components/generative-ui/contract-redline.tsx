"use client";

import { useState } from 'react';
import { FileText, Check, X, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

interface RedlineChange {
  id: string;
  type: 'deletion' | 'addition' | 'modification';
  originalText: string;
  suggestedText: string;
  reason: string;
  clauseType: string;
  accepted?: boolean;
}

interface ContractRedlineProps {
  contractName: string;
  changes: RedlineChange[];
  onAcceptChange?: (changeId: string) => void;
  onRejectChange?: (changeId: string) => void;
  onAcceptAll?: () => void;
}

const typeConfig = {
  deletion: {
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    label: 'Remove',
    icon: X,
  },
  addition: {
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    label: 'Add',
    icon: Check,
  },
  modification: {
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    label: 'Modify',
    icon: MessageSquare,
  },
};

export function ContractRedline({
  contractName,
  changes,
  onAcceptChange,
  onRejectChange,
  onAcceptAll,
}: ContractRedlineProps) {
  const [expandedChanges, setExpandedChanges] = useState<Set<string>>(new Set());
  const [localChanges, setLocalChanges] = useState<RedlineChange[]>(changes);
  
  const toggleChange = (changeId: string) => {
    const newExpanded = new Set(expandedChanges);
    if (newExpanded.has(changeId)) {
      newExpanded.delete(changeId);
    } else {
      newExpanded.add(changeId);
    }
    setExpandedChanges(newExpanded);
  };
  
  const handleAccept = (changeId: string) => {
    setLocalChanges(prev => prev.map(c => 
      c.id === changeId ? { ...c, accepted: true } : c
    ));
    onAcceptChange?.(changeId);
  };
  
  const handleReject = (changeId: string) => {
    setLocalChanges(prev => prev.map(c => 
      c.id === changeId ? { ...c, accepted: false } : c
    ));
    onRejectChange?.(changeId);
  };
  
  const pendingCount = localChanges.filter(c => c.accepted === undefined).length;
  const acceptedCount = localChanges.filter(c => c.accepted === true).length;
  const rejectedCount = localChanges.filter(c => c.accepted === false).length;
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Contract Redline
            </CardTitle>
            <p className="text-sm text-slate-400 mt-1">{contractName}</p>
          </div>
          {onAcceptAll && pendingCount > 0 && (
            <Button
              size="sm"
              variant="outline"
              className="h-7 text-xs border-green-500/30 text-green-500 hover:bg-green-500/10"
              onClick={onAcceptAll}
            >
              Accept All ({pendingCount})
            </Button>
          )}
        </div>
        
        {/* Summary badges */}
        <div className="flex gap-2 mt-3">
          <Badge variant="outline" className="border-slate-600 text-slate-400">
            {localChanges.length} Changes
          </Badge>
          {acceptedCount > 0 && (
            <Badge variant="outline" className="border-green-500/30 text-green-500">
              {acceptedCount} Accepted
            </Badge>
          )}
          {rejectedCount > 0 && (
            <Badge variant="outline" className="border-red-500/30 text-red-500">
              {rejectedCount} Rejected
            </Badge>
          )}
          {pendingCount > 0 && (
            <Badge variant="outline" className="border-yellow-500/30 text-yellow-500">
              {pendingCount} Pending
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <ScrollArea className="max-h-[400px]">
          <div className="space-y-2">
            {localChanges.map((change) => {
              const config = typeConfig[change.type];
              const Icon = config.icon;
              const isExpanded = expandedChanges.has(change.id);
              
              return (
                <Collapsible
                  key={change.id}
                  open={isExpanded}
                  onOpenChange={() => toggleChange(change.id)}
                >
                  <div
                    className={cn(
                      'rounded-lg border p-3 transition-all',
                      config.borderColor,
                      change.accepted === true && 'opacity-60',
                      change.accepted === false && 'opacity-40'
                    )}
                  >
                    <CollapsibleTrigger asChild>
                      <button className="w-full text-left">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-start gap-2 flex-1">
                            <div className={cn('p-1 rounded', config.bgColor)}>
                              <Icon className={cn('h-3 w-3', config.color)} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-sm text-white">
                                  {change.clauseType}
                                </span>
                                <Badge 
                                  variant="outline" 
                                  className={cn('text-[10px] h-4', config.color)}
                                >
                                  {config.label}
                                </Badge>
                                {change.accepted !== undefined && (
                                  <Badge 
                                    variant="outline" 
                                    className={cn(
                                      'text-[10px] h-4',
                                      change.accepted ? 'text-green-500' : 'text-red-500'
                                    )}
                                  >
                                    {change.accepted ? 'Accepted' : 'Rejected'}
                                  </Badge>
                                )}
                              </div>
                              <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">
                                {change.reason}
                              </p>
                            </div>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-slate-500" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-slate-500" />
                          )}
                        </div>
                      </button>
                    </CollapsibleTrigger>
                    
                    <CollapsibleContent className="pt-3">
                      <div className="space-y-3">
                        {/* Original text */}
                        {change.originalText && (
                          <div className="rounded bg-red-500/10 p-2 border border-red-500/20">
                            <div className="text-[10px] text-red-400 mb-1 font-medium flex items-center gap-1">
                              <X className="h-3 w-3" />
                              ORIGINAL
                            </div>
                            <p className="text-xs text-slate-300 font-mono whitespace-pre-wrap">
                              {change.originalText}
                            </p>
                          </div>
                        )}
                        
                        {/* Suggested text */}
                        {change.suggestedText && (
                          <div className="rounded bg-green-500/10 p-2 border border-green-500/20">
                            <div className="text-[10px] text-green-400 mb-1 font-medium flex items-center gap-1">
                              <Check className="h-3 w-3" />
                              SUGGESTED
                            </div>
                            <p className="text-xs text-slate-300 font-mono whitespace-pre-wrap">
                              {change.suggestedText}
                            </p>
                          </div>
                        )}
                        
                        {/* Reason */}
                        <div className="rounded bg-slate-800/50 p-2">
                          <div className="text-[10px] text-slate-500 mb-1 font-medium">
                            💡 REASON
                          </div>
                          <p className="text-xs text-slate-300">{change.reason}</p>
                        </div>
                        
                        {/* Actions */}
                        {change.accepted === undefined && (
                          <div className="flex gap-2 pt-2">
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs flex-1 border-green-500/30 text-green-500 hover:bg-green-500/10"
                              onClick={() => handleAccept(change.id)}
                            >
                              <Check className="h-3 w-3 mr-1" />
                              Accept
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-7 text-xs flex-1 border-red-500/30 text-red-500 hover:bg-red-500/10"
                              onClick={() => handleReject(change.id)}
                            >
                              <X className="h-3 w-3 mr-1" />
                              Reject
                            </Button>
                          </div>
                        )}
                      </div>
                    </CollapsibleContent>
                  </div>
                </Collapsible>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
