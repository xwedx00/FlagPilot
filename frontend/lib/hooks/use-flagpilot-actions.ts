"use client";

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { useState } from "react";

/**
 * FlagPilot CopilotKit Actions
 * ============================
 * All 6 primary actions that map to backend agent capabilities.
 * These actions are registered with CopilotKit and callable by the AI.
 */

export interface AgentState {
    status: "idle" | "planning" | "executing" | "complete" | "error";
    currentAgent: string | null;
    riskLevel: "none" | "low" | "medium" | "high" | "critical";
    agentOutputs: Record<string, string>;
    progress: number;
}

export function useFlagPilotActions() {
    const [agentState, setAgentState] = useState<AgentState>({
        status: "idle",
        currentAgent: null,
        riskLevel: "none",
        agentOutputs: {},
        progress: 0,
    });

    // ============================================
    // useCopilotReadable - Inject context for the AI
    // ============================================
    useCopilotReadable({
        description: "Current agent state and risk assessment",
        value: agentState,
    });

    useCopilotReadable({
        description: "FlagPilot capabilities",
        value: `FlagPilot is an AI platform with 17 specialized agents:
- Contract Guardian: Analyzes contracts for legal risks
- Job Authenticator: Detects scam job postings (fast-fail)
- Scope Sentinel: Identifies scope creep indicators
- Payment Enforcer: Ensures fair payment terms
- Negotiation Assistant: Provides negotiation strategies
- Communication Coach: Crafts professional responses
- Dispute Mediator: Guides conflict resolution
- Ghosting Shield: Tracks unresponsive clients
- Risk Advisor: Emergency safety protocols
The AI can analyze contracts, detect scams, identify scope creep, suggest negotiation tactics, and search the knowledge base.`,
    });

    // ============================================
    // useCopilotAction - Contract Analysis
    // ============================================
    useCopilotAction({
        name: "analyzeContract",
        description: "Analyze a freelance contract for legal risks, unfavorable terms, and red flags. Uses Contract Guardian agent.",
        parameters: [
            {
                name: "contractText",
                type: "string",
                description: "The full text of the contract to analyze",
                required: true,
            },
            {
                name: "focusAreas",
                type: "string",
                description: "Specific areas to focus on (e.g., 'payment terms', 'IP rights', 'termination')",
                required: false,
            },
        ],
        handler: async ({ contractText, focusAreas }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "contract-guardian" }));
            return `Analyzing contract with Contract Guardian agent${focusAreas ? ` focusing on: ${focusAreas}` : ""}...`;
        },
    });

    // ============================================
    // useCopilotAction - Scam Detection
    // ============================================
    useCopilotAction({
        name: "detectScam",
        description: "Check a job posting or client message for scam patterns and red flags. Uses Job Authenticator with fast-fail capability.",
        parameters: [
            {
                name: "content",
                type: "string",
                description: "The job posting, message, or offer to check for scams",
                required: true,
            },
            {
                name: "clientInfo",
                type: "string",
                description: "Any additional client information (profile, history, etc.)",
                required: false,
            },
        ],
        handler: async ({ content, clientInfo }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "job-authenticator" }));
            return `Checking for scam patterns with Job Authenticator...`;
        },
    });

    // ============================================
    // useCopilotAction - Scope Creep Detection
    // ============================================
    useCopilotAction({
        name: "detectScopeCreep",
        description: "Analyze a situation for scope creep and boundary violations. Uses Scope Sentinel agent.",
        parameters: [
            {
                name: "originalScope",
                type: "string",
                description: "The original agreed-upon scope of work",
                required: true,
            },
            {
                name: "newRequest",
                type: "string",
                description: "The new request or change being asked",
                required: true,
            },
        ],
        handler: async ({ originalScope, newRequest }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "scope-sentinel" }));
            return `Analyzing scope change with Scope Sentinel...`;
        },
    });

    // ============================================
    // useCopilotAction - Rate Negotiation
    // ============================================
    useCopilotAction({
        name: "negotiateRate",
        description: "Get negotiation strategies for freelance rates. Uses Negotiation Assistant.",
        parameters: [
            {
                name: "currentRate",
                type: "number",
                description: "Your current or offered rate",
                required: true,
            },
            {
                name: "desiredRate",
                type: "number",
                description: "Your desired rate",
                required: true,
            },
            {
                name: "context",
                type: "string",
                description: "Context about the project, client, or industry",
                required: false,
            },
        ],
        handler: async ({ currentRate, desiredRate, context }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "negotiation-assistant" }));
            return `Crafting negotiation strategy for ${currentRate} to ${desiredRate}...`;
        },
    });

    // ============================================
    // useCopilotAction - Payment Advice
    // ============================================
    useCopilotAction({
        name: "getPaymentAdvice",
        description: "Get advice for payment issues, late payments, or payment terms. Uses Payment Enforcer.",
        parameters: [
            {
                name: "situation",
                type: "string",
                description: "Description of the payment situation or issue",
                required: true,
            },
            {
                name: "amountOwed",
                type: "number",
                description: "Amount owed (optional)",
                required: false,
            },
            {
                name: "daysPastDue",
                type: "number",
                description: "Days past due date (optional)",
                required: false,
            },
        ],
        handler: async ({ situation, amountOwed, daysPastDue }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "payment-enforcer" }));
            return `Payment Enforcer analyzing situation...`;
        },
    });

    // ============================================
    // useCopilotAction - Knowledge Search
    // ============================================
    useCopilotAction({
        name: "searchKnowledge",
        description: "Search the FlagPilot knowledge base for freelance best practices, strategies, and wisdom.",
        parameters: [
            {
                name: "query",
                type: "string",
                description: "Search query for the knowledge base",
                required: true,
            },
            {
                name: "category",
                type: "string",
                description: "Category filter (contracts, payments, negotiations, scams, etc.)",
                required: false,
            },
        ],
        handler: async ({ query, category }) => {
            setAgentState(prev => ({ ...prev, status: "executing", currentAgent: "knowledge-search" }));
            return `Searching knowledge base for: ${query}...`;
        },
    });

    // ============================================
    // useCopilotChatSuggestions - Smart prompts
    // ============================================
    useCopilotChatSuggestions({
        instructions: `Based on FlagPilot's capabilities, suggest relevant next actions:
    - If no context: suggest "Analyze a contract" or "Check a job for scams"
    - If contract discussed: suggest checking specific clauses
    - If payment issue: suggest payment enforcement strategies
    - If negotiating: suggest counter-offer tactics`,
        minSuggestions: 2,
        maxSuggestions: 3,
    });

    return {
        agentState,
        setAgentState,
    };
}

export default useFlagPilotActions;
