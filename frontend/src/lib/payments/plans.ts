export interface Plan {
    id: string
    name: string
    description: string
    priceId: string // Used as productId or slug for Polar
    price: number
    features: string[]
    trialDays: number
    slug?: string
}

export const plans: Plan[] = [
    {
        id: "basic",
        name: "Basic",
        description: "Essential features for individuals",
        priceId: "3f721596-f308-4521-9972-23c3458bf2a0",
        slug: "Basic",
        price: 9.99,
        features: [
            "Access to basic features",
            "Up to 5 projects",
            "Community support"
        ],
        trialDays: 7
    },
    {
        id: "pro",
        name: "Pro",
        description: "Advanced features for professionals",
        priceId: "389146df-4610-482a-a925-8316df08479e",
        slug: "Pro",
        price: 29.99,
        features: [
            "Everything in Basic",
            "Unlimited projects",
            "Priority support",
            "Advanced caching"
        ],
        trialDays: 14
    },
    {
        id: "agency",
        name: "Agency",
        description: "For agencies and large teams",
        priceId: "17b84828-567f-4648-892f-117ed72ca808",
        slug: "Agency",
        price: 99.99,
        features: [
            "Everything in Pro",
            "Team management",
            "Custom analytics",
            "White labeling"
        ],
        trialDays: 30
    },
    {
        id: "credits-500",
        name: "500 Credits",
        description: "Top up your account credits",
        priceId: "81b181df-bd15-41db-aa3b-0a7731e1c823",
        slug: "500-Credits",
        price: 5.00,
        features: [
            "500 AI generation credits",
            "Never expire",
            "Use across all projects"
        ],
        trialDays: 0
    }
]
