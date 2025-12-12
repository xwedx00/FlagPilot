"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BillingScreen } from "@/components/billingsdk/billing-screen"
import { PricingTableSix, type PlanProps } from "@/components/billingsdk/pricing-table-six"
import { InvoiceHistory, type InvoiceItem } from "@/components/billingsdk/invoice-history"
import { UsageMeter } from "@/components/billingsdk/usage-meter"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CreditCard, Receipt, BarChart3, Settings, Zap, AlertCircle } from "lucide-react"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "sonner"

// Pricing plans configured for Polar.sh
const plans: PlanProps[] = [
    {
        id: "free",
        title: "Free",
        description: "Perfect for getting started",
        monthlyPrice: 0,
        yearlyPrice: 0,
        features: [
            "Up to 3 projects",
            "Basic analytics",
            "Community support",
            "1GB storage"
        ]
    },
    {
        id: "pro",
        title: "Pro",
        description: "For professionals and growing teams",
        monthlyPrice: 29,
        yearlyPrice: 290,
        isFeatured: true,
        features: [
            "Unlimited projects",
            "Advanced analytics",
            "Priority support",
            "100GB storage",
            "API access",
            "Custom integrations"
        ]
    },
    {
        id: "enterprise",
        title: "Enterprise",
        description: "For large organizations with custom needs",
        monthlyPrice: 99,
        yearlyPrice: 990,
        isCustom: true,
        features: [
            "Everything in Pro",
            "Dedicated support",
            "Custom SLA",
            "Unlimited storage",
            "SSO & SAML",
            "Custom contracts"
        ]
    }
]

// Sample invoices data
const invoices: InvoiceItem[] = [
    {
        id: "INV-001",
        date: "2024-12-01",
        amount: "$29.00",
        status: "paid",
        description: "Pro Plan - Monthly"
    },
    {
        id: "INV-002",
        date: "2024-11-01",
        amount: "$29.00",
        status: "paid",
        description: "Pro Plan - Monthly"
    },
    {
        id: "INV-003",
        date: "2024-10-01",
        amount: "$29.00",
        status: "paid",
        description: "Pro Plan - Monthly"
    }
]

// Sample usage data
const usageData = [
    { name: "API Requests", usage: 7500, limit: 10000 },
    { name: "Storage Used", usage: 45, limit: 100 },
    { name: "Team Members", usage: 3, limit: 10 }
]

export default function BillingPage() {
    const [activeTab, setActiveTab] = useState("overview")
    const [showCancelDialog, setShowCancelDialog] = useState(false)
    const [isCancelling, setIsCancelling] = useState(false)

    const handlePlanSelect = async (planId: string) => {
        // TODO: Integrate with Polar checkout
        toast.info(`Selected plan: ${planId} - Polar checkout integration pending`)
        console.log("Selected plan:", planId)
    }

    const handleCancelSubscription = async () => {
        setIsCancelling(true)
        try {
            // TODO: Integrate with Polar API
            await new Promise(resolve => setTimeout(resolve, 1000))
            toast.success("Subscription cancelled successfully")
            setShowCancelDialog(false)
        } catch (error) {
            toast.error("Failed to cancel subscription")
        } finally {
            setIsCancelling(false)
        }
    }

    return (
        <div className="container mx-auto space-y-6 py-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
                    <p className="text-muted-foreground">
                        Manage your subscription, view invoices, and track usage
                    </p>
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-none lg:flex">
                    <TabsTrigger value="overview" className="gap-2">
                        <CreditCard className="h-4 w-4" />
                        <span className="hidden sm:inline">Overview</span>
                    </TabsTrigger>
                    <TabsTrigger value="plans" className="gap-2">
                        <Zap className="h-4 w-4" />
                        <span className="hidden sm:inline">Plans</span>
                    </TabsTrigger>
                    <TabsTrigger value="usage" className="gap-2">
                        <BarChart3 className="h-4 w-4" />
                        <span className="hidden sm:inline">Usage</span>
                    </TabsTrigger>
                    <TabsTrigger value="invoices" className="gap-2">
                        <Receipt className="h-4 w-4" />
                        <span className="hidden sm:inline">Invoices</span>
                    </TabsTrigger>
                </TabsList>

                {/* Overview Tab */}
                <TabsContent value="overview" className="space-y-6">
                    <BillingScreen
                        planName="Pro Plan"
                        planPrice="$29/mo"
                        renewalDate="Jan 12, 2025"
                        totalBalance="$15.50"
                        username="user"
                        giftedCredits="$0.00"
                        monthlyCredits="$13.50"
                        monthlyCreditsLimit="$29.00"
                        purchasedCredits="$0.00"
                        resetDays={19}
                        autoRechargeEnabled={false}
                        onViewPlans={() => setActiveTab("plans")}
                        onCancelPlan={() => setShowCancelDialog(true)}
                        onBuyCredits={() => toast.info("Buy credits - coming soon")}
                        onEnableAutoRecharge={() => toast.info("Auto-recharge - coming soon")}
                    />

                    {/* Quick Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Settings className="h-5 w-5" />
                                Quick Actions
                            </CardTitle>
                            <CardDescription>
                                Manage your billing settings
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="flex flex-wrap gap-3">
                            <Button variant="outline" onClick={() => setActiveTab("plans")}>
                                Change Plan
                            </Button>
                            <Button variant="outline" onClick={() => setActiveTab("invoices")}>
                                View Invoices
                            </Button>
                            <Button variant="outline" onClick={() => setActiveTab("usage")}>
                                View Usage
                            </Button>
                            <Button
                                variant="destructive"
                                className="ml-auto"
                                onClick={() => setShowCancelDialog(true)}
                            >
                                Cancel Subscription
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Plans Tab */}
                <TabsContent value="plans" className="space-y-6">
                    <PricingTableSix
                        plans={plans}
                        onPlanSelect={handlePlanSelect}
                    />
                </TabsContent>

                {/* Usage Tab */}
                <TabsContent value="usage" className="space-y-6">
                    <div className="grid gap-6 md:grid-cols-2">
                        <UsageMeter
                            usage={usageData}
                            variant="circle"
                            title="Resource Usage"
                            description="Your current resource consumption"
                        />

                        <UsageMeter
                            usage={usageData}
                            variant="linear"
                            title="Usage Overview"
                            description="Your resource consumption this billing period"
                        />
                    </div>
                </TabsContent>

                {/* Invoices Tab */}
                <TabsContent value="invoices" className="space-y-6">
                    <InvoiceHistory
                        invoices={invoices}
                        onDownload={(id) => toast.info(`Downloading invoice: ${id}`)}
                    />
                </TabsContent>
            </Tabs>

            {/* Simple Cancel Subscription Dialog */}
            <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <AlertCircle className="h-5 w-5 text-destructive" />
                            Cancel Subscription
                        </DialogTitle>
                        <DialogDescription>
                            Are you sure you want to cancel your Pro Plan subscription?
                            You will lose access to premium features at the end of your billing period.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="gap-2 sm:gap-0">
                        <Button variant="outline" onClick={() => setShowCancelDialog(false)}>
                            Keep Subscription
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleCancelSubscription}
                            disabled={isCancelling}
                        >
                            {isCancelling ? "Cancelling..." : "Cancel Subscription"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
