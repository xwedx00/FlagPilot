import { Polar } from "@polar-sh/sdk"

// Initialize Polar SDK client
export const polar = new Polar({
    accessToken: process.env.POLAR_ACCESS_TOKEN,
    server: process.env.POLAR_ENVIRONMENT === "production" ? "production" : "sandbox"
})

// Organization ID for Polar
export const POLAR_ORGANIZATION_ID = process.env.POLAR_ORGANIZATION_ID!

// Helper types
export interface PolarProduct {
    id: string
    name: string
    description: string | null
    isRecurring: boolean
    prices: PolarPrice[]
}

export interface PolarPrice {
    id: string
    amountType: "fixed" | "custom" | "free"
    priceAmount?: number
    priceCurrency?: string
    recurringInterval?: "month" | "year"
}

export interface PolarSubscription {
    id: string
    status: "active" | "canceled" | "incomplete" | "past_due" | "trialing" | "unpaid"
    currentPeriodStart: Date
    currentPeriodEnd: Date
    cancelAtPeriodEnd: boolean
    product: PolarProduct
    price: PolarPrice
}

// Helper function to format price
export function formatPrice(amount: number, currency: string = "USD"): string {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency.toUpperCase()
    }).format(amount / 100)
}

// Helper to get checkout URL
export async function createCheckoutSession(options: {
    productPriceId: string
    customerId?: string
    successUrl: string
    customerEmail?: string
}): Promise<string> {
    const checkout = await polar.checkouts.create({
        productPriceId: options.productPriceId,
        successUrl: options.successUrl,
        customerEmail: options.customerEmail
    })

    return checkout.url
}

// Helper to get customer portal URL
export async function getCustomerPortalUrl(customerId: string): Promise<string> {
    const session = await polar.customerSessions.create({
        customerId
    })

    return session.customerPortalUrl
}

// Plans configuration for the app
export const polarPlans = [
    {
        id: "free",
        name: "Free",
        description: "Perfect for getting started",
        monthlyPrice: 0,
        yearlyPrice: 0,
        features: [
            "Up to 3 projects",
            "Basic analytics",
            "Community support",
            "1GB storage"
        ],
        priceId: null // Free tier, no price ID needed
    },
    {
        id: "pro",
        name: "Pro",
        description: "For professionals and growing teams",
        monthlyPrice: 29,
        yearlyPrice: 290,
        features: [
            "Unlimited projects",
            "Advanced analytics",
            "Priority support",
            "100GB storage",
            "API access",
            "Custom integrations"
        ],
        priceId: process.env.POLAR_PRO_MONTHLY_PRICE_ID,
        yearlyPriceId: process.env.POLAR_PRO_YEARLY_PRICE_ID,
        highlight: true,
        badge: "Most Popular"
    },
    {
        id: "enterprise",
        name: "Enterprise",
        description: "For large organizations with custom needs",
        monthlyPrice: "Custom",
        yearlyPrice: "Custom",
        features: [
            "Everything in Pro",
            "Dedicated support",
            "Custom SLA",
            "Unlimited storage",
            "SSO & SAML",
            "Custom contracts"
        ],
        priceId: null // Contact sales
    }
]
