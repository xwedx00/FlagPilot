import { db } from "@/db/drizzle";
import { account, session, subscription, user, verification } from "@/db/schema";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { nextCookies } from "better-auth/next-js";

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:*",
    "http://localhost:*",
  ],
  advanced: {
    crossSubDomainCookies: {
      enabled: false,
    },
    cookiePrefix: "flagpilot",
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,
    },
  },
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: {
      user,
      session,
      account,
      verification,
      subscription,
    },
  }),
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  plugins: [
    nextCookies(),
  ],
});

// Note: Polar billing integration requires these env vars:
// - POLAR_ACCESS_TOKEN
// - NEXT_PUBLIC_STARTER_TIER  
// - POLAR_WEBHOOK_SECRET
// When configured, uncomment and add polar plugin to plugins array
