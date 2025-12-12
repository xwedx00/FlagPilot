import { boolean, integer, jsonb, pgTable, real, text, timestamp, uuid } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
import { user } from "./auth.schema";

// --- USER PROFILE & PREFERENCES ---

export const userProfile = pgTable("user_profile", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .unique()
        .references(() => user.id, { onDelete: "cascade" }),
    displayName: text("display_name"),
    freelanceType: text("freelance_type"),
    experienceLevel: text("experience_level"),
    platforms: text("platforms"), // JSON array string
    bio: text("bio"),
    hourlyRate: integer("hourly_rate"),
    portfolioUrl: text("portfolio_url"),
    timezone: text("timezone"),
    language: text("language").default("en"),
    onboardingCompleted: boolean("onboarding_completed").default(false),
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const userPreferences = pgTable("user_preferences", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .unique()
        .references(() => user.id, { onDelete: "cascade" }),
    // AI Settings
    aiModel: text("ai_model").default("google/gemini-2.0-flash-001"),
    aiTemperature: text("ai_temperature").default("0.7"),
    maxTokens: integer("max_tokens").default(4096),
    // Privacy & Data
    dataRetentionDays: integer("data_retention_days").default(90),
    allowAnalytics: boolean("allow_analytics").default(true),
    allowDataSharing: boolean("allow_data_sharing").default(false),
    // Notifications
    emailNotifications: boolean("email_notifications").default(true),
    agentAlerts: boolean("agent_alerts").default(true),
    weeklyDigest: boolean("weekly_digest").default(false),
    // Theme
    theme: text("theme").default("system"),
    // Compliance
    gdprConsent: boolean("gdpr_consent").default(false),
    gdprConsentDate: timestamp("gdpr_consent_date"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

// --- INTELLIGENCE DOMAIN ---

export const project = pgTable("project", {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    description: text("description"),
    clientName: text("client_name"),
    minioPath: text("minio_path").notNull().default(""),
    status: text("status").default("active"),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
});

export const mission = pgTable("mission", {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    projectId: uuid("project_id").references(() => project.id, { onDelete: "set null" }),
    title: text("title").notNull(),
    description: text("description"),
    status: text("status").default("active"),
    workflowData: jsonb("workflow_data"),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
    completedAt: timestamp("completed_at"),
});

export const chatMessage = pgTable("chat_message", {
    id: uuid("id").primaryKey().defaultRandom(),
    missionId: uuid("mission_id").notNull().references(() => mission.id, { onDelete: "cascade" }),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    role: text("role").notNull(), // user, assistant, system
    content: text("content").notNull(),
    agentId: text("agent_id"),
    messageType: text("message_type").default("text"),
    messageMetadata: jsonb("message_metadata"),
    createdAt: timestamp("created_at").defaultNow(),
});

export const workflow = pgTable("workflow", {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    description: text("description"),
    definition: jsonb("definition").notNull(),
    isPublic: boolean("is_public").default(false),
    tags: jsonb("tags"),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
});

export const workflowExecution = pgTable("workflow_execution", {
    id: uuid("id").primaryKey().defaultRandom(),
    workflowId: uuid("workflow_id").references(() => workflow.id, { onDelete: "set null" }),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    planSnapshot: jsonb("plan_snapshot").notNull(),
    results: jsonb("results"),
    status: text("status").default("pending"),
    completedAt: timestamp("completed_at"),
    createdAt: timestamp("created_at").defaultNow(),
});

export const agentTask = pgTable("agent_task", {
    id: uuid("id").primaryKey().defaultRandom(),
    projectId: uuid("project_id").references(() => project.id, { onDelete: "set null" }),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    agentRole: text("agent_role").notNull(),
    status: text("status").default("queued"),
    inputContext: jsonb("input_context").notNull().default({}),
    outputArtifact: jsonb("output_artifact"),
    errorMessage: text("error_message"),
    costCredits: integer("cost_credits").default(0),
    createdAt: timestamp("created_at").defaultNow(),
    startedAt: timestamp("started_at"),
    completedAt: timestamp("completed_at"),
});

export const agentMemory = pgTable("agent_memory", {
    id: uuid("id").primaryKey().defaultRandom(),
    taskId: uuid("task_id").references(() => agentTask.id, { onDelete: "set null" }),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    agentRole: text("agent_role").notNull(),
    key: text("key").notNull(),
    value: text("value").notNull(),
    confidence: real("confidence").default(1.0),
    memoryType: text("memory_type").default("fact"),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
    expiresAt: timestamp("expires_at"),
});

// Using 'document_table' to avoid conflict with DOM 'document'
export const documentTable = pgTable("document", {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    projectId: uuid("project_id").references(() => project.id, { onDelete: "set null" }),
    filename: text("filename").notNull(),
    contentType: text("content_type").notNull(),
    sizeBytes: integer("size_bytes").notNull(),
    bucket: text("bucket").notNull(),
    objectKey: text("object_key").notNull(),
    processingStatus: text("processing_status").default("pending"),
    embeddingStatus: text("embedding_status").default("pending"),
    extractedText: text("extracted_text"),
    fileMetadata: jsonb("file_metadata"),
    createdAt: timestamp("created_at").defaultNow(),
    processedAt: timestamp("processed_at"),
});

// --- EXTRAS ---

export const chatHistory = pgTable("chat_history", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .references(() => user.id, { onDelete: "cascade" }),
    title: text("title"),
    messages: text("messages").notNull(), // Legacy JSON string
    agentsUsed: text("agents_used"), // JSON array string
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const knowledgeContext = pgTable("knowledge_context", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    type: text("type").notNull(),
    content: text("content").notNull(),
    metadata: text("metadata"),
    isActive: boolean("is_active").default(true),
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const usageTracking = pgTable("usage_tracking", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .references(() => user.id, { onDelete: "cascade" }),
    date: timestamp("date").notNull(),
    chatMessages: integer("chat_messages").default(0),
    agentCalls: integer("agent_calls").default(0),
    documentsAnalyzed: integer("documents_analyzed").default(0),
    tokensUsed: integer("tokens_used").default(0),
    createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const subscription = pgTable("subscription", {
    id: text("id").primaryKey(),
    createdAt: timestamp("created_at").notNull(),
    modifiedAt: timestamp("modified_at"),
    amount: integer("amount").notNull(),
    currency: text("currency").notNull(),
    recurringInterval: text("recurring_interval").notNull(),
    status: text("status").notNull(),
    currentPeriodStart: timestamp("current_period_start").notNull(),
    currentPeriodEnd: timestamp("current_period_end").notNull(),
    cancelAtPeriodEnd: boolean("cancel_at_period_end").notNull().default(false),
    canceledAt: timestamp("canceled_at"),
    startedAt: timestamp("started_at").notNull(),
    endsAt: timestamp("ends_at"),
    endedAt: timestamp("ended_at"),
    customerId: text("customer_id").notNull(),
    productId: text("product_id").notNull(),
    discountId: text("discount_id"),
    checkoutId: text("checkout_id").notNull(),
    customerCancellationReason: text("customer_cancellation_reason"),
    customerCancellationComment: text("customer_cancellation_comment"),
    metadata: text("metadata"),
    customFieldData: text("custom_field_data"),
    userId: text("user_id").references(() => user.id),
});

export const creditWallet = pgTable("credit_wallet", {
    id: text("id").primaryKey(),
    userId: text("user_id")
        .notNull()
        .unique()
        .references(() => user.id, { onDelete: "cascade" }),
    balance: integer("balance").notNull().default(0),
    createdAt: timestamp("created_at").notNull().defaultNow(),
    updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const creditTransaction = pgTable("credit_transaction", {
    id: text("id").primaryKey(),
    walletId: text("wallet_id")
        .notNull()
        .references(() => creditWallet.id, { onDelete: "cascade" }),
    amount: integer("amount").notNull(),
    description: text("description").notNull(),
    referenceId: text("reference_id"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
});
