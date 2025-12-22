"use client";

import { useCoAgentStateRender } from "@copilotkit/react-core";
import { Bot, Shield, AlertTriangle, CheckCircle, Loader2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Agent Status Types
 */
interface FlagPilotAgentState {
    status: "idle" | "planning" | "executing" | "agent_complete" | "complete" | "error";
    currentAgent: string | null;
    riskLevel: "none" | "low" | "medium" | "high" | "critical";
    agents?: string[];
    error?: string;
}

/**
 * Agent display mapping
 */
const AGENT_INFO: Record<string, { name: string; emoji: string; description: string }> = {
    "contract-guardian": { name: "Contract Guardian", emoji: "⚖️", description: "Analyzing legal risks..." },
    "job-authenticator": { name: "Job Authenticator", emoji: "🔍", description: "Scanning for scam patterns..." },
    "scope-sentinel": { name: "Scope Sentinel", emoji: "🎯", description: "Checking scope boundaries..." },
    "payment-enforcer": { name: "Payment Enforcer", emoji: "💰", description: "Reviewing payment terms..." },
    "negotiation-assistant": { name: "Negotiation Assistant", emoji: "🤝", description: "Crafting strategies..." },
    "communication-coach": { name: "Communication Coach", emoji: "💬", description: "Composing response..." },
    "dispute-mediator": { name: "Dispute Mediator", emoji: "⚔️", description: "Analyzing conflict..." },
    "ghosting-shield": { name: "Ghosting Shield", emoji: "👻", description: "Tracking client..." },
    "risk-advisor": { name: "Risk Advisor", emoji: "🚨", description: "Assessing critical risks..." },
    "orchestrator": { name: "Orchestrator", emoji: "🎯", description: "Coordinating team..." },
    "knowledge-search": { name: "Knowledge Base", emoji: "📚", description: "Searching wisdom..." },
};

/**
 * Risk Level Badge Component
 */
function RiskBadge({ level }: { level: FlagPilotAgentState["riskLevel"] }) {
    const config = {
        none: { bg: "bg-zinc-100", text: "text-zinc-600", label: "No Risk" },
        low: { bg: "bg-green-100", text: "text-green-700", label: "Low Risk" },
        medium: { bg: "bg-yellow-100", text: "text-yellow-700", label: "Medium Risk" },
        high: { bg: "bg-orange-100", text: "text-orange-700", label: "High Risk" },
        critical: { bg: "bg-red-100", text: "text-red-700", label: "Critical Risk" },
    };

    const { bg, text, label } = config[level] || config.none;

    if (level === "none") return null;

    return (
        <span className={cn("px-2 py-0.5 rounded-full text-xs font-medium", bg, text)}>
            {level === "critical" && <AlertTriangle className="w-3 h-3 inline mr-1" />}
            {label}
        </span>
    );
}

/**
 * Active Agent Card Component
 */
function ActiveAgentCard({ agentId }: { agentId: string }) {
    const info = AGENT_INFO[agentId] || { name: agentId, emoji: "🤖", description: "Working..." };

    return (
        <div className="flex items-center gap-3 p-3 bg-indigo-50 dark:bg-indigo-950/30 rounded-lg border border-indigo-200 dark:border-indigo-800 animate-pulse">
            <div className="text-2xl">{info.emoji}</div>
            <div className="flex-1 min-w-0">
                <div className="font-medium text-indigo-900 dark:text-indigo-100">{info.name}</div>
                <div className="text-xs text-indigo-600 dark:text-indigo-400 truncate">{info.description}</div>
            </div>
            <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
        </div>
    );
}

/**
 * Agent Status Display - Main component
 * Renders the current state of the FlagPilot agent system
 */
export function AgentStatusDisplay({ state }: { state: FlagPilotAgentState }) {
    const { status, currentAgent, riskLevel, error } = state;

    // Don't show anything for idle state
    if (status === "idle") return null;

    return (
        <div className="space-y-2 mb-4">
            {/* Header with status */}
            <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                    {status === "complete" ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : status === "error" ? (
                        <XCircle className="w-4 h-4 text-red-500" />
                    ) : (
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
                    )}
                    <span className="text-zinc-600 dark:text-zinc-400">
                        {status === "planning" && "Planning analysis..."}
                        {status === "executing" && "Agents working..."}
                        {status === "complete" && "Analysis complete"}
                        {status === "error" && "Error occurred"}
                    </span>
                </div>
                <RiskBadge level={riskLevel} />
            </div>

            {/* Active Agent Card */}
            {currentAgent && status === "executing" && (
                <ActiveAgentCard agentId={currentAgent} />
            )}

            {/* Error Display */}
            {error && (
                <div className="p-3 bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex items-center gap-2 text-red-700 dark:text-red-400 text-sm">
                        <AlertTriangle className="w-4 h-4" />
                        {error}
                    </div>
                </div>
            )}
        </div>
    );
}

/**
 * Hook to render agent state in chat
 * Uses CopilotKit's useCoAgentStateRender
 */
export function useAgentStatusRenderer() {
    useCoAgentStateRender<FlagPilotAgentState>({
        name: "flagpilot_orchestrator",
        render: ({ status, state, nodeName }) => {
            // Don't render for idle or complete without risk
            if (!state || state.status === "idle") return null;

            return <AgentStatusDisplay state={state} />;
        },
    });
}

export default AgentStatusDisplay;
