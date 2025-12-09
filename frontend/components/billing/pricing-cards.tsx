"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Check, Zap, Crown, Building2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface PricingPlan {
  id: string
  name: string
  description: string
  price: number
  credits: number
  features: string[]
  popular?: boolean
  icon: React.ReactNode
}

const PLANS: PricingPlan[] = [
  {
    id: "free",
    name: "Starter",
    description: "For trying out FlagPilot",
    price: 0,
    credits: 50,
    icon: <Zap className="w-5 h-5" />,
    features: [
      "50 credits/month",
      "3 agents available",
      "Basic contract review",
      "Email support",
    ],
  },
  {
    id: "pro",
    name: "Professional",
    description: "For serious freelancers",
    price: 29,
    credits: 500,
    popular: true,
    icon: <Crown className="w-5 h-5" />,
    features: [
      "500 credits/month",
      "All 13 agents",
      "Deep contract analysis",
      "Client vetting (Iris)",
      "Negotiation strategies",
      "Priority support",
      "Personal Data Moat",
    ],
  },
  {
    id: "enterprise",
    name: "Agency",
    description: "For teams and agencies",
    price: 99,
    credits: 2000,
    icon: <Building2 className="w-5 h-5" />,
    features: [
      "2,000 credits/month",
      "All 13 agents",
      "Team collaboration",
      "Custom workflows",
      "API access",
      "Dedicated support",
      "White-label options",
    ],
  },
]

interface PricingCardsProps {
  currentPlan?: string
  onSelectPlan?: (planId: string) => void
  className?: string
}

export function PricingCards({ currentPlan, onSelectPlan, className }: PricingCardsProps) {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly")
  const yearlyDiscount = 0.8 // 20% off
  
  return (
    <div className={cn("space-y-6", className)}>
      {/* Billing Toggle */}
      <div className="flex items-center justify-center gap-4">
        <Button
          variant={billingCycle === "monthly" ? "default" : "ghost"}
          size="sm"
          onClick={() => setBillingCycle("monthly")}
          className="font-mono text-xs"
        >
          Monthly
        </Button>
        <Button
          variant={billingCycle === "yearly" ? "default" : "ghost"}
          size="sm"
          onClick={() => setBillingCycle("yearly")}
          className="font-mono text-xs"
        >
          Yearly
          <Badge variant="secondary" className="ml-2 text-[10px] bg-emerald-500/20 text-emerald-400">
            -20%
          </Badge>
        </Button>
      </div>
      
      {/* Plan Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {PLANS.map((plan) => {
          const price = billingCycle === "yearly" 
            ? Math.round(plan.price * 12 * yearlyDiscount) 
            : plan.price
          const isCurrentPlan = currentPlan === plan.id
          
          return (
            <Card 
              key={plan.id}
              className={cn(
                "relative border-zinc-800 bg-zinc-900/50 transition-all",
                plan.popular && "border-emerald-500/50 shadow-lg shadow-emerald-500/10",
                isCurrentPlan && "ring-2 ring-emerald-500"
              )}
            >
              {plan.popular && (
                <Badge 
                  className="absolute -top-3 left-1/2 -translate-x-1/2 bg-emerald-500 text-white text-[10px]"
                >
                  MOST POPULAR
                </Badge>
              )}
              
              <CardHeader>
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "p-2 rounded-sm",
                    plan.id === "free" && "bg-zinc-800 text-zinc-400",
                    plan.id === "pro" && "bg-emerald-500/20 text-emerald-400",
                    plan.id === "enterprise" && "bg-violet-500/20 text-violet-400",
                  )}>
                    {plan.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg font-mono">{plan.name}</CardTitle>
                    <CardDescription className="text-xs">{plan.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* Price */}
                <div>
                  <span className="text-4xl font-mono font-bold text-zinc-100">
                    ${price}
                  </span>
                  <span className="text-zinc-500 text-sm">
                    /{billingCycle === "yearly" ? "year" : "month"}
                  </span>
                  <p className="text-xs text-emerald-400 mt-1 font-mono">
                    {plan.credits.toLocaleString()} credits included
                  </p>
                </div>
                
                {/* Features */}
                <ul className="space-y-2">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <Check className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                      <span className="text-zinc-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              
              <CardFooter>
                <Button
                  className={cn(
                    "w-full font-mono text-sm",
                    plan.popular 
                      ? "bg-emerald-600 hover:bg-emerald-700" 
                      : plan.id === "enterprise"
                        ? "bg-violet-600 hover:bg-violet-700"
                        : ""
                  )}
                  variant={plan.id === "free" ? "outline" : "default"}
                  onClick={() => onSelectPlan?.(plan.id)}
                  disabled={isCurrentPlan}
                >
                  {isCurrentPlan ? "Current Plan" : plan.price === 0 ? "Get Started" : "Upgrade"}
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
      
      {/* Credit Packs */}
      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader>
          <CardTitle className="text-sm font-mono">Need More Credits?</CardTitle>
          <CardDescription>Top up anytime with credit packs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {[
              { credits: 100, price: 10 },
              { credits: 500, price: 40 },
              { credits: 1000, price: 70 },
            ].map((pack) => (
              <Button
                key={pack.credits}
                variant="outline"
                className="flex flex-col h-auto py-4 border-zinc-700 hover:border-emerald-500/50"
                onClick={() => onSelectPlan?.(`topup-${pack.credits}`)}
              >
                <span className="text-xl font-mono font-bold text-emerald-400">
                  {pack.credits}
                </span>
                <span className="text-xs text-zinc-500">credits</span>
                <span className="text-sm font-mono mt-2">${pack.price}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
