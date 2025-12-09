"use client";

import { useState } from 'react';
import { 
  MessageSquare, 
  Copy, 
  Check, 
  ChevronRight,
  Target,
  Shield,
  Zap,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface TalkingPoint {
  id: string;
  point: string;
  rationale: string;
  priority: 'high' | 'medium' | 'low';
}

interface NegotiationStrategy {
  id: string;
  name: string;
  description: string;
  tone: 'aggressive' | 'collaborative' | 'accommodating';
  openingStatement: string;
  talkingPoints: TalkingPoint[];
  fallbackPosition: string;
  walkAwayPoint: string;
}

interface NegotiationScriptProps {
  clientName: string;
  negotiationType: string; // e.g., "Rate Negotiation", "Contract Terms"
  currentOffer?: string;
  targetOutcome?: string;
  strategies: NegotiationStrategy[];
  leverage: string[];
  risks: string[];
}

const toneConfig = {
  aggressive: {
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    icon: Zap,
    label: 'Aggressive',
  },
  collaborative: {
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    icon: ThumbsUp,
    label: 'Collaborative',
  },
  accommodating: {
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    icon: Shield,
    label: 'Accommodating',
  },
};

const priorityConfig = {
  high: { color: 'text-red-500', label: 'Must Have' },
  medium: { color: 'text-yellow-500', label: 'Important' },
  low: { color: 'text-slate-400', label: 'Nice to Have' },
};

export function NegotiationScript({
  clientName,
  negotiationType,
  currentOffer,
  targetOutcome,
  strategies,
  leverage,
  risks,
}: NegotiationScriptProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState(strategies[0]?.id);
  
  const copyToClipboard = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedId(null), 2000);
  };
  
  const activeStrategy = strategies.find(s => s.id === selectedStrategy) || strategies[0];
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              Negotiation Strategy
            </CardTitle>
            <p className="text-sm text-slate-400 mt-1">
              {negotiationType} with {clientName}
            </p>
          </div>
        </div>
        
        {/* Current situation */}
        {(currentOffer || targetOutcome) && (
          <div className="grid grid-cols-2 gap-2 mt-3">
            {currentOffer && (
              <div className="rounded-lg bg-slate-800/50 p-2">
                <div className="text-[10px] text-slate-500 mb-0.5">Current Offer</div>
                <div className="text-sm font-semibold text-white">{currentOffer}</div>
              </div>
            )}
            {targetOutcome && (
              <div className="rounded-lg bg-green-500/10 border border-green-500/20 p-2">
                <div className="text-[10px] text-green-400 mb-0.5">Target</div>
                <div className="text-sm font-semibold text-green-400">{targetOutcome}</div>
              </div>
            )}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="pt-0 space-y-4">
        {/* Strategy selector */}
        <div>
          <div className="text-xs text-slate-500 mb-2">Choose your approach:</div>
          <div className="flex gap-2">
            {strategies.map((strategy) => {
              const config = toneConfig[strategy.tone];
              const Icon = config.icon;
              const isSelected = selectedStrategy === strategy.id;
              
              return (
                <button
                  key={strategy.id}
                  onClick={() => setSelectedStrategy(strategy.id)}
                  className={cn(
                    'flex-1 rounded-lg border p-2 transition-all text-left',
                    isSelected 
                      ? `${config.borderColor} ${config.bgColor}` 
                      : 'border-slate-700 hover:border-slate-600'
                  )}
                >
                  <div className="flex items-center gap-1.5 mb-1">
                    <Icon className={cn('h-3.5 w-3.5', config.color)} />
                    <span className={cn('text-xs font-medium', isSelected ? config.color : 'text-slate-300')}>
                      {strategy.name}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500 line-clamp-2">
                    {strategy.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
        
        {activeStrategy && (
          <Tabs defaultValue="script" className="w-full">
            <TabsList className="w-full bg-slate-800/50">
              <TabsTrigger value="script" className="flex-1 text-xs">Script</TabsTrigger>
              <TabsTrigger value="points" className="flex-1 text-xs">Talking Points</TabsTrigger>
              <TabsTrigger value="intel" className="flex-1 text-xs">Intel</TabsTrigger>
            </TabsList>
            
            {/* Script Tab */}
            <TabsContent value="script" className="mt-3 space-y-3">
              {/* Opening statement */}
              <div className="rounded-lg bg-primary/10 border border-primary/20 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] text-primary font-medium">OPENING STATEMENT</div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                    onClick={() => copyToClipboard(activeStrategy.openingStatement, 'opening')}
                  >
                    {copiedId === 'opening' ? (
                      <Check className="h-3 w-3 text-green-500" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <p className="text-sm text-slate-200 italic">
                  "{activeStrategy.openingStatement}"
                </p>
              </div>
              
              {/* Fallback position */}
              <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] text-yellow-400 font-medium">FALLBACK POSITION</div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                    onClick={() => copyToClipboard(activeStrategy.fallbackPosition, 'fallback')}
                  >
                    {copiedId === 'fallback' ? (
                      <Check className="h-3 w-3 text-green-500" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-slate-300">
                  {activeStrategy.fallbackPosition}
                </p>
              </div>
              
              {/* Walk away point */}
              <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
                <div className="text-[10px] text-red-400 font-medium mb-1">🚫 WALK AWAY IF</div>
                <p className="text-xs text-slate-300">
                  {activeStrategy.walkAwayPoint}
                </p>
              </div>
            </TabsContent>
            
            {/* Talking Points Tab */}
            <TabsContent value="points" className="mt-3">
              <div className="space-y-2">
                {activeStrategy.talkingPoints.map((point, index) => {
                  const priority = priorityConfig[point.priority];
                  
                  return (
                    <div 
                      key={point.id}
                      className="rounded-lg bg-slate-800/50 p-3 border border-slate-700/50"
                    >
                      <div className="flex items-start gap-2">
                        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-700 text-[10px] font-bold text-slate-300">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm text-white font-medium">
                              {point.point}
                            </p>
                            <Badge 
                              variant="outline" 
                              className={cn('text-[10px] h-4', priority.color)}
                            >
                              {priority.label}
                            </Badge>
                          </div>
                          <p className="text-xs text-slate-400">
                            {point.rationale}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(point.point, point.id)}
                        >
                          {copiedId === point.id ? (
                            <Check className="h-3 w-3 text-green-500" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </TabsContent>
            
            {/* Intel Tab */}
            <TabsContent value="intel" className="mt-3 space-y-3">
              {/* Leverage */}
              <div className="rounded-lg bg-green-500/10 border border-green-500/20 p-3">
                <div className="text-[10px] text-green-400 font-medium mb-2 flex items-center gap-1">
                  <ThumbsUp className="h-3 w-3" />
                  YOUR LEVERAGE
                </div>
                <ul className="space-y-1">
                  {leverage.map((item, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-1">
                      <ChevronRight className="h-3 w-3 text-green-500 mt-0.5 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Risks */}
              <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
                <div className="text-[10px] text-red-400 font-medium mb-2 flex items-center gap-1">
                  <ThumbsDown className="h-3 w-3" />
                  WATCH OUT FOR
                </div>
                <ul className="space-y-1">
                  {risks.map((item, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-1">
                      <ChevronRight className="h-3 w-3 text-red-500 mt-0.5 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}
