-- Manual migration for SaaS-grade user schema fields
-- Run this to add subscription, credits, and usage tracking to user table

-- Create enum types (if they don't exist)
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'pro', 'enterprise', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE subscription_tier AS ENUM ('free', 'starter', 'professional', 'enterprise');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add new columns to user table
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS "role" user_role DEFAULT 'user' NOT NULL,
ADD COLUMN IF NOT EXISTS "subscription_tier" subscription_tier DEFAULT 'free' NOT NULL,
ADD COLUMN IF NOT EXISTS "credits_balance" integer DEFAULT 100 NOT NULL,
ADD COLUMN IF NOT EXISTS "credits_used_this_month" integer DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS "credits_reset_at" timestamp,
ADD COLUMN IF NOT EXISTS "stripe_customer_id" text,
ADD COLUMN IF NOT EXISTS "stripe_subscription_id" text,
ADD COLUMN IF NOT EXISTS "subscription_status" text,
ADD COLUMN IF NOT EXISTS "current_period_end" timestamp,
ADD COLUMN IF NOT EXISTS "total_agent_calls" integer DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS "last_agent_call_at" timestamp;

-- Create index on stripe_customer_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_user_stripe_customer_id ON "user" (stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;

-- Create index on subscription_tier for analytics
CREATE INDEX IF NOT EXISTS idx_user_subscription_tier ON "user" (subscription_tier);
