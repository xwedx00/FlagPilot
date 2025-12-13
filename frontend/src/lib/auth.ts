import { betterAuth } from "better-auth"
import { drizzleAdapter } from "better-auth/adapters/drizzle"
import { db } from "@/database/db"
import * as schema from "@/database/schema"
import { polar, checkout, portal } from "@polar-sh/better-auth"
import { Polar } from "@polar-sh/sdk"

const polarClient = new Polar({
    accessToken: process.env.POLAR_ACCESS_TOKEN,
    server: process.env.POLAR_ENVIRONMENT === "production" ? "production" : "sandbox"
})

export const auth = betterAuth({
    database: drizzleAdapter(db, {
        provider: "pg",
        usePlural: false, // Our schema uses singular table names (user, session, account)
        schema
    }),
    plugins: [
        polar({
            client: polarClient,
            createCustomerOnSignUp: true,
            use: [
                checkout({
                    products: [
                        {
                            productId: "81b181df-bd15-41db-aa3b-0a7731e1c823",
                            slug: "500-Credits" // Custom slug for easy reference in Checkout URL, e.g. /checkout/500-Credits
                        },
                        {
                            productId: "9db74830-ecdc-473e-80ea-a91c4c8bdea9",
                            slug: "Agency" // Custom slug for easy reference in Checkout URL, e.g. /checkout/Agency
                        },
                        {
                            productId: "d430cb9c-530d-457b-bbe9-0c06ba9685fb",
                            slug: "Pro" // Custom slug for easy reference in Checkout URL, e.g. /checkout/Pro
                        },
                        {
                            productId: "36982d04-d330-4d48-9d15-754d490d80ec",
                            slug: "Basic" // Custom slug for easy reference in Checkout URL, e.g. /checkout/Basic
                        }
                    ],
                    successUrl: process.env.POLAR_SUCCESS_URL,
                    authenticatedUsersOnly: true
                }),
                portal()
            ],
        })
    ],
    // OAuth-only authentication - no email/password
    socialProviders: {
        github: {
            clientId: process.env.GITHUB_CLIENT_ID as string,
            clientSecret: process.env.GITHUB_CLIENT_SECRET as string
        },
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID as string,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET as string
        }
    }
})

