import { createServerOnlyFn } from "@tanstack/react-start";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { betterAuth } from "better-auth/minimal";
import { tanstackStartCookies } from "better-auth/tanstack-start";

import { env } from "~/env/server";
import { db } from "~/lib/db";

const getAuthConfig = createServerOnlyFn(() =>
  betterAuth({
    baseURL: env.VITE_BASE_URL,
    trustedOrigins: [
      env.VITE_BASE_URL,
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
    telemetry: {
      enabled: false,
    },
    database: drizzleAdapter(db, {
      provider: "pg",
    }),

    // https://www.better-auth.com/docs/integrations/tanstack#usage-tips
    plugins: [tanstackStartCookies()],

    // https://www.better-auth.com/docs/concepts/session-management#session-caching
    session: {
      cookieCache: {
        enabled: true,
        maxAge: 5 * 60, // 5 minutes
      },
    },

    // https://www.better-auth.com/docs/concepts/oauth
    socialProviders: {
      github: {
        clientId: env.GITHUB_CLIENT_ID!,
        clientSecret: env.GITHUB_CLIENT_SECRET!,
      },
      google: {
        clientId: env.GOOGLE_CLIENT_ID!,
        clientSecret: env.GOOGLE_CLIENT_SECRET!,
      },
    },

    // https://www.better-auth.com/docs/authentication/email-password
    // Disabled - only social providers (GitHub/Google)
    emailAndPassword: {
      enabled: false,
    },

    experimental: {
      // https://www.better-auth.com/docs/adapters/drizzle#joins-experimental
      joins: true,
    },
  }),
);

export const auth = getAuthConfig();
