
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "@/db/schema";
import { nextCookies } from "better-auth/next-js";

// Database Setup
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
});
export const db = drizzle(pool, { schema });

// Better Auth Setup
export const auth = betterAuth({
    database: drizzleAdapter(db, {
        provider: "pg",
        schema: schema,
    }),
    emailAndPassword: {
        enabled: false, // Disabled as per requirement
    },
    socialProviders: {
        github: {
            clientId: process.env.GITHUB_CLIENT_ID!,
            clientSecret: process.env.GITHUB_CLIENT_SECRET!,
        },
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }
    },
    account: {
        accountLinking: {
            enabled: false, // Explicitly disable linking to ensure "denied" behavior for same email
        },
    },
    plugins: [nextCookies()], // Use Next.js cookies plugin
});
