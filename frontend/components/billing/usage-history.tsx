"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ArrowDownRight, ArrowUpRight, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

interface UsageEntry {
  id: string
  timestamp: Date
  type: "usage" | "grant" | "refund" | "bonus"
  amount: number
  description: string
  agentId?: string
  referenceId?: string
}

interface UsageHistoryProps {
  entries: UsageEntry[]
  className?: string
  maxHeight?: number
}

const AGENT_ICONS: Record<string, string> = {
  "contract-guardian": "🦅",
  "legal-eagle": "🦅",
  "job-authenticator": "🔍",
  "payment-enforcer": "💰",
  "negotiator": "🎯",
  "iris": "👁️",
  "adjudicator": "⚖️",
  "scope-sentinel": "📏",
  "coach": "🏆",
  "sentinel": "🛡️",
  "ledger": "📊",
  "scribe": "📝",
  "connector": "💬",
  "vault-keeper": "🔐",
  "flagpilot": "🚀",
}

export function UsageHistory({ entries, className, maxHeight = 400 }: UsageHistoryProps) {
  // Group entries by date
  const groupedEntries = useMemo(() => {
    const groups: Record<string, UsageEntry[]> = {}
    
    entries.forEach((entry) => {
      const date = entry.timestamp.toLocaleDateString()
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(entry)
    })
    
    return groups
  }, [entries])
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
  }
  
  return (
    <Card className={cn("border-zinc-800 bg-zinc-900/50", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-mono tracking-wide">USAGE HISTORY</CardTitle>
        <CardDescription className="text-xs">
          Recent credit transactions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea style={{ maxHeight }}>
          {entries.length === 0 ? (
            <div className="py-8 text-center text-zinc-500 text-sm">
              No transactions yet
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedEntries).map(([date, dayEntries]) => (
                <div key={date}>
                  <h4 className="text-xs font-mono text-zinc-500 mb-2 sticky top-0 bg-zinc-900 py-1">
                    {date}
                  </h4>
                  <div className="space-y-1">
                    {dayEntries.map((entry) => (
                      <div
                        key={entry.id}
                        className="flex items-center justify-between py-2 px-2 rounded-sm hover:bg-zinc-800/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          {/* Icon */}
                          <div className={cn(
                            "w-8 h-8 rounded-sm flex items-center justify-center text-sm",
                            entry.amount > 0 
                              ? "bg-emerald-500/20 text-emerald-400" 
                              : "bg-zinc-800 text-zinc-400"
                          )}>
                            {entry.agentId 
                              ? AGENT_ICONS[entry.agentId] || "🤖"
                              : entry.amount > 0 
                                ? <ArrowUpRight className="w-4 h-4" /> 
                                : <ArrowDownRight className="w-4 h-4" />
                            }
                          </div>
                          
                          {/* Details */}
                          <div>
                            <p className="text-sm text-zinc-200">{entry.description}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-[10px] text-zinc-500 font-mono">
                                {formatTime(entry.timestamp)}
                              </span>
                              {entry.agentId && (
                                <Badge variant="outline" className="text-[10px] py-0 px-1.5">
                                  {entry.agentId}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Amount */}
                        <span className={cn(
                          "font-mono text-sm font-bold",
                          entry.amount > 0 ? "text-emerald-400" : "text-zinc-400"
                        )}>
                          {entry.amount > 0 ? "+" : ""}{entry.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

// Demo data generator
export function generateDemoUsageHistory(): UsageEntry[] {
  const now = new Date()
  const entries: UsageEntry[] = []
  
  // Add some demo entries
  const demoData = [
    { type: "usage" as const, amount: -25, description: "Contract Review", agentId: "contract-guardian" },
    { type: "usage" as const, amount: -15, description: "Client Research", agentId: "iris" },
    { type: "usage" as const, amount: -5, description: "Job Verification", agentId: "job-authenticator" },
    { type: "grant" as const, amount: 500, description: "Monthly subscription credits" },
    { type: "usage" as const, amount: -20, description: "Negotiation Strategy", agentId: "negotiator" },
    { type: "usage" as const, amount: -2, description: "Email Draft", agentId: "connector" },
    { type: "bonus" as const, amount: 50, description: "Welcome bonus" },
  ]
  
  demoData.forEach((data, i) => {
    entries.push({
      id: `entry-${i}`,
      timestamp: new Date(now.getTime() - i * 3600000 * (i + 1)),
      ...data,
    })
  })
  
  return entries
}
