CREATE TYPE "public"."subscription_tier" AS ENUM('free', 'starter', 'professional', 'enterprise');--> statement-breakpoint
CREATE TYPE "public"."user_role" AS ENUM('user', 'pro', 'enterprise', 'admin');--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "role" "user_role" DEFAULT 'user';--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "subscriptionTier" "subscription_tier" DEFAULT 'free';--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "creditsBalance" integer DEFAULT 100;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "creditsUsedThisMonth" integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "creditsResetAt" timestamp;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "stripeCustomerId" text;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "stripeSubscriptionId" text;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "subscriptionStatus" text;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "currentPeriodEnd" timestamp;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "totalAgentCalls" integer DEFAULT 0;--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "lastAgentCallAt" timestamp;