"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { useState, useCallback } from "react";

/**
 * FlagPilot CopilotKit Actions - Complete 17 Agent Integration
 * =============================================================
 * All agent actions + memory system actions for production-ready integration.
 */

export interface AgentState {
    status: "idle" | "planning" | "executing" | "complete" | "error";
    currentAgent: string | null;
    riskLevel: "none" | "low" | "medium" | "high" | "critical";
    agentOutputs: Record<string, string>;
    progress: number;
}

export interface UserProfile {
    userId: string;
    summary: string;
    preferences: Record<string, any>;
    riskTolerance: string;
}

export function useFlagPilotActions() {
    const [agentState, setAgentState] = useState<AgentState>({
        status: "idle",
        currentAgent: null,
        riskLevel: "none",
        agentOutputs: {},
        progress: 0,
    });

    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

    // ============================================
    // useCopilotReadable - Inject context for the AI
    // ============================================
    useCopilotReadable({
        description: "Current agent state and risk assessment",
        value: agentState,
    });

    useCopilotReadable({
        description: "User profile and preferences",
        value: userProfile,
    });

    useCopilotReadable({
        description: "FlagPilot platform capabilities - 17 specialized AI agents",
        value: `FlagPilot is an AI-powered freelancer protection platform with 17 specialized agents:

CORE PROTECTION AGENTS:
- Contract Guardian: Analyzes contracts for legal risks, unfavorable terms, and red flags
- Job Authenticator: Detects scam job postings with fast-fail capability
- Scope Sentinel: Identifies scope creep and boundary violations
- Payment Enforcer: Ensures fair payment terms and helps with collection
- Risk Advisor: Emergency safety protocols for high-risk situations

COMMUNICATION AGENTS:
- Communication Coach: Crafts professional client responses and messages
- Negotiation Assistant: Provides rate negotiation strategies and counter-offers
- Dispute Mediator: Guides through conflict resolution processes
- Ghosting Shield: Tracks unresponsive clients and provides follow-up strategies

ANALYSIS AGENTS:
- Profile Analyzer: Analyzes client history and reputation
- Application Filter: Filters job applications based on criteria and red flags
- Talent Vet: Vets potential collaborators and subcontractors
- Feedback Loop: Analyzes outcomes to improve future recommendations
- Planner Role: Breaks down complex requests into actionable steps

KNOWLEDGE SYSTEM:
- RAGFlow Search: Searches the global knowledge base of freelance best practices
- Memory System: Tracks user preferences, chat history, and shared experiences
- Global Wisdom: Aggregated insights from successful freelancers`,
    });

    // ============================================
    // AGENT 1: Contract Guardian
    // ============================================
    useCopilotAction({
        name: "analyzeContract",
        description: "Analyze a freelance contract for legal risks, unfavorable terms, and red flags. Uses Contract Guardian agent.",
        parameters: [
            { name: "contractText", type: "string", description: "The full text of the contract to analyze", required: true },
            { name: "focusAreas", type: "string", description: "Specific areas to focus on (e.g., 'payment terms', 'IP rights', 'termination')", required: false },
        ],
        handler: async ({ contractText, focusAreas }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "contract-guardian" }));
            return `Analyzing contract with Contract Guardian${focusAreas ? ` focusing on: ${focusAreas}` : ""}...`;
        },
    });

    // ============================================
    // AGENT 2: Job Authenticator
    // ============================================
    useCopilotAction({
        name: "detectScam",
        description: "Check a job posting or client message for scam patterns and red flags. Uses Job Authenticator with fast-fail capability.",
        parameters: [
            { name: "content", type: "string", description: "The job posting, message, or offer to check for scams", required: true },
            { name: "clientInfo", type: "string", description: "Any additional client information (profile, history, etc.)", required: false },
        ],
        handler: async ({ content, clientInfo }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "job-authenticator" }));
            return `Checking for scam patterns with Job Authenticator...`;
        },
    });

    // ============================================
    // AGENT 3: Scope Sentinel
    // ============================================
    useCopilotAction({
        name: "detectScopeCreep",
        description: "Analyze a situation for scope creep and boundary violations. Uses Scope Sentinel agent.",
        parameters: [
            { name: "originalScope", type: "string", description: "The original agreed-upon scope of work", required: true },
            { name: "newRequest", type: "string", description: "The new request or change being asked", required: true },
        ],
        handler: async ({ originalScope, newRequest }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "scope-sentinel" }));
            return `Analyzing scope change with Scope Sentinel...`;
        },
    });

    // ============================================
    // AGENT 4: Payment Enforcer
    // ============================================
    useCopilotAction({
        name: "getPaymentAdvice",
        description: "Get advice for payment issues, late payments, or payment terms. Uses Payment Enforcer.",
        parameters: [
            { name: "situation", type: "string", description: "Description of the payment situation or issue", required: true },
            { name: "amountOwed", type: "number", description: "Amount owed in dollars", required: false },
            { name: "daysPastDue", type: "number", description: "Days past due date", required: false },
        ],
        handler: async ({ situation, amountOwed, daysPastDue }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "payment-enforcer" }));
            return `Payment Enforcer analyzing situation...`;
        },
    });

    // ============================================
    // AGENT 5: Negotiation Assistant
    // ============================================
    useCopilotAction({
        name: "negotiateRate",
        description: "Get negotiation strategies for freelance rates. Uses Negotiation Assistant.",
        parameters: [
            { name: "currentRate", type: "number", description: "Your current or offered rate", required: true },
            { name: "desiredRate", type: "number", description: "Your desired rate", required: true },
            { name: "context", type: "string", description: "Context about the project, client, or industry", required: false },
        ],
        handler: async ({ currentRate, desiredRate, context }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "negotiation-assistant" }));
            return `Crafting negotiation strategy for rate increase...`;
        },
    });

    // ============================================
    // AGENT 6: Communication Coach
    // ============================================
    useCopilotAction({
        name: "craftMessage",
        description: "Craft a professional client message or response. Uses Communication Coach.",
        parameters: [
            { name: "context", type: "string", description: "Context of the conversation or situation", required: true },
            { name: "messageType", type: "string", description: "Type: 'response', 'follow-up', 'boundary-setting', 'introduction', 'negotiation'", required: true },
            { name: "tone", type: "string", description: "Desired tone: 'professional', 'friendly', 'firm', 'apologetic'", required: false },
        ],
        handler: async ({ context, messageType, tone }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "communication-coach" }));
            return `Communication Coach crafting ${messageType} message...`;
        },
    });

    // ============================================
    // AGENT 7: Dispute Mediator
    // ============================================
    useCopilotAction({
        name: "resolveDispute",
        description: "Get guidance for resolving a client dispute or conflict. Uses Dispute Mediator.",
        parameters: [
            { name: "disputeDescription", type: "string", description: "Description of the dispute or conflict", required: true },
            { name: "yourPosition", type: "string", description: "Your side of the story and desired outcome", required: true },
            { name: "clientPosition", type: "string", description: "The client's position (if known)", required: false },
        ],
        handler: async ({ disputeDescription, yourPosition, clientPosition }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "dispute-mediator" }));
            return `Dispute Mediator analyzing conflict...`;
        },
    });

    // ============================================
    // AGENT 8: Ghosting Shield
    // ============================================
    useCopilotAction({
        name: "handleGhosting",
        description: "Get strategies for handling an unresponsive or ghosting client. Uses Ghosting Shield.",
        parameters: [
            { name: "situation", type: "string", description: "Description of the ghosting situation", required: true },
            { name: "lastContact", type: "string", description: "When was the last contact with the client", required: true },
            { name: "outstandingWork", type: "string", description: "Any outstanding deliverables or payments", required: false },
        ],
        handler: async ({ situation, lastContact, outstandingWork }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "ghosting-shield" }));
            return `Ghosting Shield analyzing client behavior...`;
        },
    });

    // ============================================
    // AGENT 9: Profile Analyzer
    // ============================================
    useCopilotAction({
        name: "analyzeClientProfile",
        description: "Analyze a client's profile, history, and reputation. Uses Profile Analyzer.",
        parameters: [
            { name: "profileInfo", type: "string", description: "Client profile information to analyze", required: true },
            { name: "platform", type: "string", description: "Platform where the client is (Upwork, Fiverr, direct, etc.)", required: false },
        ],
        handler: async ({ profileInfo, platform }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "profile-analyzer" }));
            return `Profile Analyzer examining client...`;
        },
    });

    // ============================================
    // AGENT 10: Application Filter
    // ============================================
    useCopilotAction({
        name: "filterJobs",
        description: "Filter and evaluate job postings based on your criteria and detect red flags. Uses Application Filter.",
        parameters: [
            { name: "jobPostings", type: "string", description: "Job posting(s) to evaluate", required: true },
            { name: "preferences", type: "string", description: "Your job preferences (rate, type, industry, etc.)", required: false },
            { name: "dealBreakers", type: "string", description: "Your deal-breakers or red flags to watch for", required: false },
        ],
        handler: async ({ jobPostings, preferences, dealBreakers }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "application-filter" }));
            return `Application Filter evaluating jobs...`;
        },
    });

    // ============================================
    // AGENT 11: Talent Vet
    // ============================================
    useCopilotAction({
        name: "vetCandidate",
        description: "Vet a potential collaborator, subcontractor, or team member. Uses Talent Vet.",
        parameters: [
            { name: "candidateInfo", type: "string", description: "Information about the candidate to evaluate", required: true },
            { name: "roleRequirements", type: "string", description: "Requirements for the role they would fill", required: true },
        ],
        handler: async ({ candidateInfo, roleRequirements }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "talent-vet" }));
            return `Talent Vet evaluating candidate...`;
        },
    });

    // ============================================
    // AGENT 12: Risk Advisor
    // ============================================
    useCopilotAction({
        name: "assessRisk",
        description: "Get emergency risk assessment and safety protocols. Uses Risk Advisor for critical situations.",
        parameters: [
            { name: "situation", type: "string", description: "Description of the potentially risky situation", required: true },
            { name: "urgency", type: "string", description: "Urgency level: 'low', 'medium', 'high', 'critical'", required: false },
        ],
        handler: async ({ situation, urgency }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "risk-advisor", riskLevel: (urgency as any) || "medium" }));
            return `Risk Advisor assessing situation...`;
        },
    });

    // ============================================
    // AGENT 13: Feedback Loop
    // ============================================
    useCopilotAction({
        name: "submitFeedback",
        description: "Submit feedback on a completed interaction to improve future recommendations. Uses Feedback Loop.",
        parameters: [
            { name: "interactionSummary", type: "string", description: "Summary of the interaction or project", required: true },
            { name: "outcome", type: "string", description: "How it turned out: 'success', 'partial', 'failure'", required: true },
            { name: "lessonLearned", type: "string", description: "Key lesson or insight from this experience", required: false },
        ],
        handler: async ({ interactionSummary, outcome, lessonLearned }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "feedback-loop" }));
            return `Feedback Loop recording experience...`;
        },
    });

    // ============================================
    // AGENT 14: Planner Role
    // ============================================
    useCopilotAction({
        name: "planProject",
        description: "Break down a complex project or request into actionable steps. Uses Planner Role.",
        parameters: [
            { name: "projectDescription", type: "string", description: "Description of the project or task to plan", required: true },
            { name: "constraints", type: "string", description: "Any constraints (timeline, budget, resources)", required: false },
        ],
        handler: async ({ projectDescription, constraints }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "planner-role" }));
            return `Planner breaking down project...`;
        },
    });

    // ============================================
    // KNOWLEDGE: RAGFlow Search
    // ============================================
    useCopilotAction({
        name: "searchKnowledge",
        description: "Search the FlagPilot knowledge base for freelance best practices, strategies, and wisdom.",
        parameters: [
            { name: "query", type: "string", description: "Search query for the knowledge base", required: true },
            { name: "category", type: "string", description: "Category: 'contracts', 'payments', 'negotiations', 'scams', 'communication'", required: false },
        ],
        handler: async ({ query, category }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "knowledge-search" }));
            return `Searching knowledge base for: ${query}...`;
        },
    });

    // ============================================
    // MEMORY: Search Global Wisdom
    // ============================================
    useCopilotAction({
        name: "searchWisdom",
        description: "Search aggregated insights and wisdom from successful freelancers.",
        parameters: [
            { name: "topic", type: "string", description: "Topic to search for wisdom on", required: true },
        ],
        handler: async ({ topic }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "wisdom-search" }));
            return `Searching global wisdom for: ${topic}...`;
        },
    });

    // ============================================
    // MEMORY: Search Similar Experiences
    // ============================================
    useCopilotAction({
        name: "findSimilarCases",
        description: "Find similar cases and experiences from other freelancers that match your situation.",
        parameters: [
            { name: "situation", type: "string", description: "Your current situation to find similar cases for", required: true },
        ],
        handler: async ({ situation }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "experience-search" }));
            return `Finding similar experiences...`;
        },
    });

    // ============================================
    // MEMORY: Get Chat History
    // ============================================
    useCopilotAction({
        name: "recallPreviousConversation",
        description: "Recall information from previous conversations or sessions.",
        parameters: [
            { name: "topic", type: "string", description: "Topic or keyword to search in chat history", required: true },
        ],
        handler: async ({ topic }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "memory-recall" }));
            return `Searching conversation history for: ${topic}...`;
        },
    });

    // ============================================
    // useCopilotChatSuggestions - Smart prompts
    // ============================================
    useCopilotChatSuggestions({
        instructions: `Based on FlagPilot's 17 specialized agents, suggest relevant actions:
    - For new users: "Analyze a contract" or "Check a job for scams"
    - If discussing a contract: suggest specific clause analysis
    - If payment issues: suggest Payment Enforcer strategies
    - If client communication: suggest Communication Coach
    - If negotiating: suggest Negotiation Assistant tactics
    - If ghosting: suggest Ghosting Shield follow-up
    - If dispute: suggest Dispute Mediator guidance`,
        minSuggestions: 2,
        maxSuggestions: 4,
    });

    return {
        agentState,
        setAgentState,
        userProfile,
        setUserProfile,
    };
}

export default useFlagPilotActions;
