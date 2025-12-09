"use client";

import { AlertTriangle, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

interface Risk {
  id: string;
  clause: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  suggestion: string;
  originalText?: string;
  suggestedText?: string;
}

interface RiskAssessmentCardProps {
  contractName: string;
  riskScore: number;
  risks: Risk[];
  onAcceptRisk?: (riskId: string) => void;
  onRejectRisk?: (riskId: string) => void;
  onAcceptSuggestion?: (riskId: string) => void;
}

const severityConfig = {
  critical: {
    color: 'bg-red-500',
    textColor: 'text-red-500',
    borderColor: 'border-red-500/30',
    bgColor: 'bg-red-500/10',
    icon: XCircle,
    label: 'Critical',
  },
  high: {
    color: 'bg-orange-500',
    textColor: 'text-orange-500',
    borderColor: 'border-orange-500/30',
    bgColor: 'bg-orange-500/10',
    icon: AlertTriangle,
    label: 'High',
  },
  medium: {
    color: 'bg-yellow-500',
    textColor: 'text-yellow-500',
    borderColor: 'border-yellow-500/30',
    bgColor: 'bg-yellow-500/10',
    icon: AlertTriangle,
    label: 'Medium',
  },
  low: {
    color: 'bg-blue-500',
    textColor: 'text-blue-500',
    borderColor: 'border-blue-500/30',
    bgColor: 'bg-blue-500/10',
    icon: CheckCircle2,
    label: 'Low',
  },
};

export function RiskAssessmentCard({
  contractName,
  riskScore,
  risks,
  onAcceptRisk,
  onRejectRisk,
  onAcceptSuggestion,
}: RiskAssessmentCardProps) {
  const [expandedRisks, setExpandedRisks] = useState<Set<string>>(new Set());
  
  const toggleRisk = (riskId: string) => {
    const newExpanded = new Set(expandedRisks);
    if (newExpanded.has(riskId)) {
      newExpanded.delete(riskId);
    } else {
      newExpanded.add(riskId);
    }
    setExpandedRisks(newExpanded);
  };
  
  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-500';
    if (score >= 60) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };
  
  const getRiskScoreLabel = (score: number) => {
    if (score >= 80) return 'High Risk';
    if (score >= 60) return 'Moderate Risk';
    if (score >= 40) return 'Low Risk';
    return 'Safe';
  };
  
  const criticalCount = risks.filter((r) => r.severity === 'critical').length;
  const highCount = risks.filter((r) => r.severity === 'high').length;
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <span className="text-2xl">🦅</span>
              Legal Eagle Analysis
            </CardTitle>
            <p className="text-sm text-slate-400 mt-1">{contractName}</p>
          </div>
          <div className="text-right">
            <div className={cn('text-2xl font-bold', getRiskScoreColor(riskScore))}>
              {riskScore}
            </div>
            <div className="text-xs text-slate-500">{getRiskScoreLabel(riskScore)}</div>
          </div>
        </div>
        
        {/* Risk summary badges */}
        <div className="flex gap-2 mt-3">
          {criticalCount > 0 && (
            <Badge variant="outline" className="border-red-500/30 text-red-500">
              {criticalCount} Critical
            </Badge>
          )}
          {highCount > 0 && (
            <Badge variant="outline" className="border-orange-500/30 text-orange-500">
              {highCount} High
            </Badge>
          )}
          <Badge variant="outline" className="border-slate-500/30 text-slate-400">
            {risks.length} Total Issues
          </Badge>
        </div>
        
        {/* Risk score bar */}
        <div className="mt-3">
          <Progress 
            value={riskScore} 
            className="h-2"
            // Custom color based on score
          />
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2">
          {risks.map((risk) => {
            const config = severityConfig[risk.severity];
            const Icon = config.icon;
            const isExpanded = expandedRisks.has(risk.id);
            
            return (
              <Collapsible
                key={risk.id}
                open={isExpanded}
                onOpenChange={() => toggleRisk(risk.id)}
              >
                <div
                  className={cn(
                    'rounded-lg border p-3 transition-colors',
                    config.borderColor,
                    config.bgColor
                  )}
                >
                  <CollapsibleTrigger asChild>
                    <button className="w-full text-left">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-2">
                          <Icon className={cn('h-4 w-4 mt-0.5', config.textColor)} />
                          <div>
                            <div className="font-medium text-sm text-white">
                              {risk.clause}
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">
                              {risk.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className={cn('text-[10px]', config.textColor)}>
                            {config.label}
                          </Badge>
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-slate-500" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-slate-500" />
                          )}
                        </div>
                      </div>
                    </button>
                  </CollapsibleTrigger>
                  
                  <CollapsibleContent className="pt-3">
                    <div className="space-y-3">
                      <p className="text-sm text-slate-300">{risk.description}</p>
                      
                      {risk.originalText && (
                        <div className="rounded bg-red-500/10 p-2 border border-red-500/20">
                          <div className="text-[10px] text-red-400 mb-1 font-medium">
                            ORIGINAL CLAUSE
                          </div>
                          <p className="text-xs text-slate-300 font-mono">
                            {risk.originalText}
                          </p>
                        </div>
                      )}
                      
                      {risk.suggestedText && (
                        <div className="rounded bg-green-500/10 p-2 border border-green-500/20">
                          <div className="text-[10px] text-green-400 mb-1 font-medium">
                            SUGGESTED REVISION
                          </div>
                          <p className="text-xs text-slate-300 font-mono">
                            {risk.suggestedText}
                          </p>
                        </div>
                      )}
                      
                      <div className="rounded bg-slate-800/50 p-2">
                        <div className="text-[10px] text-slate-500 mb-1 font-medium">
                          💡 RECOMMENDATION
                        </div>
                        <p className="text-xs text-slate-300">{risk.suggestion}</p>
                      </div>
                      
                      {/* Actions */}
                      <div className="flex gap-2 pt-2">
                        {risk.suggestedText && onAcceptSuggestion && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs border-green-500/30 text-green-500 hover:bg-green-500/10"
                            onClick={() => onAcceptSuggestion(risk.id)}
                          >
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Accept Revision
                          </Button>
                        )}
                        {onAcceptRisk && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 text-xs text-slate-400"
                            onClick={() => onAcceptRisk(risk.id)}
                          >
                            Accept Risk
                          </Button>
                        )}
                      </div>
                    </div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
