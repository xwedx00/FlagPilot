"use client";

import { 
  Building2, 
  Globe, 
  Users, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  DollarSign,
  Star,
  ExternalLink,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface ClientDossierCardProps {
  clientName: string;
  companyName?: string;
  industry?: string;
  website?: string;
  financialHealth: number; // 0-100
  reputationScore: number; // 0-100
  paymentHistory?: {
    onTime: number;
    late: number;
    average: number; // days
  };
  redFlags: string[];
  greenFlags: string[];
  linkedinUrl?: string;
  crunchbaseUrl?: string;
  glassdoorRating?: number;
  employeeCount?: string;
  fundingStage?: string;
}

export function ClientDossierCard({
  clientName,
  companyName,
  industry,
  website,
  financialHealth,
  reputationScore,
  paymentHistory,
  redFlags,
  greenFlags,
  linkedinUrl,
  crunchbaseUrl,
  glassdoorRating,
  employeeCount,
  fundingStage,
}: ClientDossierCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-500';
    if (score >= 50) return 'text-yellow-500';
    if (score >= 25) return 'text-orange-500';
    return 'text-red-500';
  };
  
  const getScoreLabel = (score: number) => {
    if (score >= 75) return 'Excellent';
    if (score >= 50) return 'Good';
    if (score >= 25) return 'Fair';
    return 'Poor';
  };
  
  const overallScore = Math.round((financialHealth + reputationScore) / 2);
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <span className="text-2xl">👁️</span>
              Iris Deep Research
            </CardTitle>
            <div className="mt-2">
              <h3 className="text-lg font-semibold text-white">{clientName}</h3>
              {companyName && (
                <p className="text-sm text-slate-400">{companyName}</p>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className={cn('text-3xl font-bold', getScoreColor(overallScore))}>
              {overallScore}
            </div>
            <div className="text-xs text-slate-500">{getScoreLabel(overallScore)}</div>
          </div>
        </div>
        
        {/* Quick info badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          {industry && (
            <Badge variant="outline" className="border-slate-600">
              <Building2 className="h-3 w-3 mr-1" />
              {industry}
            </Badge>
          )}
          {employeeCount && (
            <Badge variant="outline" className="border-slate-600">
              <Users className="h-3 w-3 mr-1" />
              {employeeCount}
            </Badge>
          )}
          {fundingStage && (
            <Badge variant="outline" className="border-slate-600">
              <DollarSign className="h-3 w-3 mr-1" />
              {fundingStage}
            </Badge>
          )}
          {glassdoorRating && (
            <Badge variant="outline" className="border-slate-600">
              <Star className="h-3 w-3 mr-1 text-yellow-500" />
              {glassdoorRating}/5
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Score breakdown */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg bg-slate-800/50 p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-400">Financial Health</span>
              <span className={cn('text-sm font-semibold', getScoreColor(financialHealth))}>
                {financialHealth}%
              </span>
            </div>
            <Progress value={financialHealth} className="h-1.5" />
          </div>
          
          <div className="rounded-lg bg-slate-800/50 p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-400">Reputation</span>
              <span className={cn('text-sm font-semibold', getScoreColor(reputationScore))}>
                {reputationScore}%
              </span>
            </div>
            <Progress value={reputationScore} className="h-1.5" />
          </div>
        </div>
        
        {/* Payment history */}
        {paymentHistory && (
          <div className="rounded-lg bg-slate-800/50 p-3">
            <div className="text-xs text-slate-400 mb-2 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Payment History
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-lg font-semibold text-green-500">
                  {paymentHistory.onTime}
                </div>
                <div className="text-[10px] text-slate-500">On Time</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-orange-500">
                  {paymentHistory.late}
                </div>
                <div className="text-[10px] text-slate-500">Late</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-slate-300">
                  {paymentHistory.average}d
                </div>
                <div className="text-[10px] text-slate-500">Avg. Days</div>
              </div>
            </div>
          </div>
        )}
        
        {/* Flags */}
        <div className="grid grid-cols-2 gap-3">
          {/* Red Flags */}
          {redFlags.length > 0 && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
              <div className="text-xs text-red-400 mb-2 flex items-center gap-1 font-medium">
                <AlertTriangle className="h-3 w-3" />
                Red Flags ({redFlags.length})
              </div>
              <ul className="space-y-1">
                {redFlags.map((flag, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-1">
                    <span className="text-red-500 mt-0.5">•</span>
                    {flag}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Green Flags */}
          {greenFlags.length > 0 && (
            <div className="rounded-lg bg-green-500/10 border border-green-500/20 p-3">
              <div className="text-xs text-green-400 mb-2 flex items-center gap-1 font-medium">
                <CheckCircle2 className="h-3 w-3" />
                Green Flags ({greenFlags.length})
              </div>
              <ul className="space-y-1">
                {greenFlags.map((flag, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-1">
                    <span className="text-green-500 mt-0.5">•</span>
                    {flag}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        {/* External links */}
        <div className="flex gap-2 pt-2">
          {website && (
            <a
              href={website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-primary transition-colors"
            >
              <Globe className="h-3 w-3" />
              Website
              <ExternalLink className="h-2.5 w-2.5" />
            </a>
          )}
          {linkedinUrl && (
            <a
              href={linkedinUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-primary transition-colors"
            >
              LinkedIn
              <ExternalLink className="h-2.5 w-2.5" />
            </a>
          )}
          {crunchbaseUrl && (
            <a
              href={crunchbaseUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-primary transition-colors"
            >
              Crunchbase
              <ExternalLink className="h-2.5 w-2.5" />
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
