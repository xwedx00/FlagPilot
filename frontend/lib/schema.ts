import { pgTable, text, timestamp, boolean, integer, pgEnum } from "drizzle-orm/pg-core";

/**
 * User role enum for access control
 */
export const userRoleEnum = pgEnum("user_role", ["user", "pro", "enterprise", "admin"]);

/**
 * Subscription tier enum for billing
 */
export const subscriptionTierEnum = pgEnum("subscription_tier", ["free", "starter", "professional", "enterprise"]);

/**
 * User table with SaaS-grade fields
 * - role: Access control level
 * - subscriptionTier: Billing tier
 * - creditsBalance: AI usage credits
 * - stripeCustomerId: Payment integration
 */
export const user = pgTable("user", {
    id: text("id").primaryKey(),
    name: text("name").notNull(),
    email: text("email").notNull().unique(),
    emailVerified: boolean("email_verified").notNull(),
    image: text("image"),
    createdAt: timestamp("created_at").notNull(),
    updatedAt: timestamp("updated_at").notNull(),

    // SaaS Fields
    role: userRoleEnum("role").default("user").notNull(),
    subscriptionTier: subscriptionTierEnum("subscription_tier").default("free").notNull(),
    creditsBalance: integer("credits_balance").default(100).notNull(), // Free tier starts with 100 credits
    creditsUsedThisMonth: integer("credits_used_this_month").default(0).notNull(),
    creditsResetAt: timestamp("credits_reset_at"),

    // Billing
    stripeCustomerId: text("stripe_customer_id"),
    stripeSubscriptionId: text("stripe_subscription_id"),
    subscriptionStatus: text("subscription_status"), // 'active', 'canceled', 'past_due'
    currentPeriodEnd: timestamp("current_period_end"),

    // Usage tracking
    totalAgentCalls: integer("total_agent_calls").default(0).notNull(),
    lastAgentCallAt: timestamp("last_agent_call_at"),
});

export const session = pgTable("session", {
    id: text("id").primaryKey(),
    expiresAt: timestamp("expires_at").notNull(),
    token: text("token").notNull().unique(),
    createdAt: timestamp("created_at").notNull(),
    updatedAt: timestamp("updated_at").notNull(),
    ipAddress: text("ip_address"),
    userAgent: text("user_agent"),
    userId: text("user_id").notNull().references(() => user.id),
});

export const account = pgTable("account", {
    id: text("id").primaryKey(),
    accountId: text("account_id").notNull(),
    providerId: text("provider_id").notNull(),
    userId: text("user_id").notNull().references(() => user.id),
    accessToken: text("access_token"),
    refreshToken: text("refresh_token"),
    idToken: text("id_token"),
    accessTokenExpiresAt: timestamp("access_token_expires_at"),
    refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
    scope: text("scope"),
    password: text("password"),
    createdAt: timestamp("created_at").notNull(),
    updatedAt: timestamp("updated_at").notNull(),
});

export const verification = pgTable("verification", {
    id: text("id").primaryKey(),
    identifier: text("identifier").notNull(),
    value: text("value").notNull(),
    expiresAt: timestamp("expires_at").notNull(),
    createdAt: timestamp("created_at"),
    updatedAt: timestamp("updated_at"),
});
