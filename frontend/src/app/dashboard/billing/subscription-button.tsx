"use client"
import { Button } from "@/components/ui/button"
import type { Plan } from "@/lib/payments/plans"
import { authClient } from "@/lib/auth-client"
import { toast } from "sonner"
import { useState } from "react"

interface SubscriptionButtonProps {
    buttonText: string
    plan: Plan
    activeSub?: any
    subId?: string
}

export default function SubscriptionButton({
    buttonText,
    plan,
    activeSub,
    subId
}: SubscriptionButtonProps) {
    const [isPending, setIsPending] = useState(false)

    const handleSubscription = async () => {
        try {
            setIsPending(true)

            // Polar Billing Integration
            // Use slug if available for prettier URLs, otherwise use priceId (productId)
            const checkoutProps = plan.slug
                ? { slug: plan.slug }
                : { products: [plan.priceId] };

            await authClient.checkout(checkoutProps)

            // Checkout handles redirect, but just in case
        } catch (err) {
            console.log(err)
            toast.error("Failed to initiate checkout")
            setIsPending(false)
        }
    }

    // Determine if this is the current plan
    // Note: This logic depends on activeSub structure, which is passed from parent.
    // If activeSub.plan === plan.name, we are on this plan.
    // But parent handles rendering "Current Plan" text or button. 
    // This button implies we want to switch TO this plan or subscribe.

    return (
        <Button
            onClick={handleSubscription}
            disabled={isPending}
        >
            {isPending ? "Processing..." : buttonText}
        </Button>
    )
}
