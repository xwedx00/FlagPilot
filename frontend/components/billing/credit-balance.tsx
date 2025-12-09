"use client"

import { useState, useEffect } from "react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Zap, TrendingUp, AlertTriangle, Sparkles } from "lucide-react"
import { cn } from "@/lib/utils"

interface CreditBalanceProps {
  credits: number
  maxCredits?: number
  plan?: "free" | "pro" | "enterprise"
  className?: string
  compact?: boolean
  onTopUp?: () => void
}

const PLAN_COLORS = {
  free: "bg-zinc-500",
  pro: "bg-emerald-500",
  enterprise: "bg-violet-500",
}

const PLAN_LABELS = {
  free: "Free",
  pro: "Pro",
  enterprise: "Enterprise",
}

export function CreditBalance({
  credits,
  maxCredits = 500,
  plan = "free",
  className,
  compact = false,
  onTopUp,
}: CreditBalanceProps) {
  const percentage = Math.min((credits / maxCredits) * 100, 100)
  const isLow = credits < maxCredits * 0.2
  const isEmpty = credits <= 0
  
  if (compact) {
    return (
      <div className={cn("px-3 py-2", className)}>
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-zinc-400 font-mono">CREDITS</span>
          <span className={cn(
            "font-mono font-bold",
            isEmpty ? "text-red-400" : isLow ? "text-amber-400" : "text-zinc-100"
          )}>
            {credits.toLocaleString()}
          </span>
        </div>
        <Progress 
          value={percentage} 
          className="h-1.5 bg-zinc-800"
        />
        {isLow && (
          <Button 
            size="sm" 
            variant="ghost"
            onClick={onTopUp}
            className="w-full mt-2 h-7 text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10"
          >
            <Zap className="w-3 h-3 mr-1" />
            Refill
          </Button>
        )}
      </div>
    )
  }
  
  return (
    <Card className={cn("border-zinc-800 bg-zinc-900/50", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-mono tracking-wide">
            CREDIT BALANCE
          </CardTitle>
          <Badge 
            variant="outline" 
            className={cn("text-[10px] uppercase", PLAN_COLORS[plan], "text-white border-none")}
          >
            {PLAN_LABELS[plan]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Balance Display */}
        <div className="flex items-end justify-between">
          <div>
            <span className={cn(
              "text-4xl font-mono font-bold",
              isEmpty ? "text-red-400" : isLow ? "text-amber-400" : "text-emerald-400"
            )}>
              {credits.toLocaleString()}
            </span>
            <span className="text-zinc-500 text-sm ml-2">/ {maxCredits.toLocaleString()}</span>
          </div>
          {isLow && !isEmpty && (
            <div className="flex items-center text-amber-400 text-xs">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Low balance
            </div>
          )}
          {isEmpty && (
            <div className="flex items-center text-red-400 text-xs">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Empty
            </div>
          )}
        </div>
        
        {/* Progress Bar */}
        <Progress 
          value={percentage} 
          className="h-2 bg-zinc-800"
        />
        
        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 pt-2">
          <div className="space-y-1">
            <p className="text-xs text-zinc-500">This Month</p>
            <p className="text-sm font-mono text-zinc-300">
              <TrendingUp className="w-3 h-3 inline mr-1 text-emerald-400" />
              {(maxCredits - credits).toLocaleString()} used
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-zinc-500">Renews</p>
            <p className="text-sm font-mono text-zinc-300">
              {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button 
            onClick={onTopUp}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 font-mono text-xs"
            size="sm"
          >
            <Zap className="w-3 h-3 mr-1" />
            Top Up
          </Button>
          {plan === "free" && (
            <Button 
              variant="outline"
              className="flex-1 border-violet-500/50 text-violet-400 hover:bg-violet-500/10 font-mono text-xs"
              size="sm"
            >
              <Sparkles className="w-3 h-3 mr-1" />
              Upgrade
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Sidebar version
export function SidebarCredits({ credits, maxCredits = 500 }: { credits: number; maxCredits?: number }) {
  const percentage = Math.min((credits / maxCredits) * 100, 100)
  const isLow = credits < maxCredits * 0.2
  
  return (
    <div className="px-4 py-3 bg-zinc-900 rounded-sm border border-zinc-800">
      <div className="flex justify-between text-xs mb-2">
        <span className="text-zinc-500 font-mono">Credits</span>
        <span className={cn(
          "font-mono font-bold",
          isLow ? "text-amber-400" : "text-zinc-100"
        )}>
          {credits.toLocaleString()}
        </span>
      </div>
      <Progress 
        value={percentage} 
        className="h-1.5 bg-zinc-800"
      />
      {isLow && (
        <Button 
          size="sm" 
          variant="secondary" 
          className="w-full mt-3 h-7 text-xs bg-zinc-800 hover:bg-zinc-700"
        >
          Refill Balance
        </Button>
      )}
    </div>
  )
}
