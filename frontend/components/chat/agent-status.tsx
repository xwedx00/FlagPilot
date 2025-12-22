"use client";

import { useCoAgentStateRender } from "@copilotkit/react-core";
import { AlertTriangle, CheckCircle, Loader2, XCircle, Shield, FileSearch, Target, DollarSign, MessageSquare, Users, Ghost, Search, Filter, UserCheck, Lightbulb, ListTodo, BookOpen, Brain } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Agent Status Types
 */
interface FlagPilotAgentState {
    status: "idle" | "planning" | "executing" | "agent_complete" | "complete" | "error" | "COMPLETED" | "ABORTED_ON_RISK";
    currentAgent: string | null;
    riskLevel: "none" | "low" | "medium" | "high" | "critical";
    agents?: string[];
    error?: string;
}

/**
 * Complete agent display mapping for all 17 agents + extras
 */
const AGENT_INFO: Record<string, { name: string; emoji: string; description: string; icon?: any }> = {
    // Core Protection Agents
    "contract-guardian": {
        name: "Contract Guardian",
        emoji: "⚖️",
        description: "Analyzing legal risks...",
        icon: FileSearch,
    },
    "job-authenticator": {
        name: "Job Authenticator",
        emoji: "🔍",
        description: "Scanning for scam patterns...",
        icon: Search,
    },
    "scope-sentinel": {
        name: "Scope Sentinel",
        emoji: "🎯",
        description: "Checking scope boundaries...",
        icon: Target,
    },
    "payment-enforcer": {
        name: "Payment Enforcer",
        emoji: "💰",
        description: "Reviewing payment terms...",
        icon: DollarSign,
    },
    "risk-advisor": {
        name: "Risk Advisor",
        emoji: "🚨",
        description: "Assessing critical risks...",
        icon: AlertTriangle,
    },

    // Communication Agents
    "communication-coach": {
        name: "Communication Coach",
        emoji: "💬",
        description: "Crafting professional message...",
        icon: MessageSquare,
    },
    "negotiation-assistant": {
        name: "Negotiation Assistant",
        emoji: "🤝",
        description: "Preparing negotiation strategies...",
        icon: Users,
    },
    "dispute-mediator": {
        name: "Dispute Mediator",
        emoji: "⚔️",
        description: "Analyzing conflict resolution...",
        icon: Shield,
    },
    "ghosting-shield": {
        name: "Ghosting Shield",
        emoji: "👻",
        description: "Tracking client response...",
        icon: Ghost,
    },

    // Analysis Agents
    "profile-analyzer": {
        name: "Profile Analyzer",
        emoji: "👤",
        description: "Analyzing client profile...",
        icon: UserCheck,
    },
    "application-filter": {
        name: "Application Filter",
        emoji: "📋",
        description: "Filtering job applications...",
        icon: Filter,
    },
    "talent-vet": {
        name: "Talent Vet",
        emoji: "🎭",
        description: "Vetting candidate...",
        icon: UserCheck,
    },
    "feedback-loop": {
        name: "Feedback Loop",
        emoji: "🔄",
        description: "Recording experience...",
        icon: Lightbulb,
    },
    "planner-role": {
        name: "Planner",
        emoji: "📝",
        description: "Breaking down project...",
        icon: ListTodo,
    },

    // Orchestration
    "orchestrator": {
        name: "Orchestrator",
        emoji: "🎯",
        description: "Coordinating team...",
        icon: Brain,
    },
    "flagpilot-orchestrator": {
        name: "FlagPilot Orchestrator",
        emoji: "🚀",
        description: "Coordinating agents...",
        icon: Brain,
    },

    // Knowledge & Memory
    "knowledge-search": {
        name: "Knowledge Base",
        emoji: "📚",
        description: "Searching wisdom...",
        icon: BookOpen,
    },
    "wisdom-search": {
        name: "Global Wisdom",
        emoji: "💡",
        description: "Finding insights...",
        icon: Lightbulb,
    },
    "experience-search": {
        name: "Experience Gallery",
        emoji: "🎨",
        description: "Finding similar cases...",
        icon: Search,
    },
    "memory-recall": {
        name: "Memory",
        emoji: "🧠",
        description: "Recalling history...",
        icon: Brain,
    },
};

/**
 * Risk Level Badge Component
 */
function RiskBadge({ level }: { level: FlagPilotAgentState["riskLevel"] }) {
    const config = {
        none: { bg: "bg-zinc-100 dark:bg-zinc-800", text: "text-zinc-600 dark:text-zinc-400", label: "No Risk" },
        low: { bg: "bg-green-100 dark:bg-green-900/30", text: "text-green-700 dark:text-green-400", label: "Low Risk" },
        medium: { bg: "bg-yellow-100 dark:bg-yellow-900/30", text: "text-yellow-700 dark:text-yellow-400", label: "Medium Risk" },
        high: { bg: "bg-orange-100 dark:bg-orange-900/30", text: "text-orange-700 dark:text-orange-400", label: "High Risk" },
        critical: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400", label: "Critical Risk" },
    };

    const { bg, text, label } = config[level] || config.none;

    if (level === "none") return null;

    return (
        <span className={cn("px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1", bg, text)}>
            {(level === "high" || level === "critical") && <AlertTriangle className="w-3 h-3" />}
            {label}
        </span>
    );
}

/**
 * Active Agent Card Component
 */
function ActiveAgentCard({ agentId }: { agentId: string }) {
    const info = AGENT_INFO[agentId] || { name: agentId, emoji: "🤖", description: "Working...", icon: Brain };
    const IconComponent = info.icon || Brain;

    return (
        <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/40 dark:to-purple-950/40 rounded-xl border border-indigo-200 dark:border-indigo-800 shadow-sm">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-white dark:bg-zinc-800 shadow-inner flex items-center justify-center">
                <span className="text-2xl">{info.emoji}</span>
            </div>
            <div className="flex-1 min-w-0">
                <div className="font-semibold text-indigo-900 dark:text-indigo-100 flex items-center gap-2">
                    {info.name}
                    <span className="flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-indigo-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                    </span>
                </div>
                <div className="text-sm text-indigo-600 dark:text-indigo-400 truncate">{info.description}</div>
            </div>
            <Loader2 className="w-5 h-5 animate-spin text-indigo-500 flex-shrink-0" />
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
        <div className="space-y-3 mb-4">
            {/* Header with status */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                    {status === "complete" || status === "COMPLETED" ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : status === "error" || status === "ABORTED_ON_RISK" ? (
                        <XCircle className="w-4 h-4 text-red-500" />
                    ) : (
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
                    )}
                    <span className="text-zinc-600 dark:text-zinc-400 font-medium">
                        {status === "planning" && "Planning analysis..."}
                        {status === "executing" && "Agents working..."}
                        {(status === "complete" || status === "COMPLETED") && "Analysis complete"}
                        {status === "error" && "Error occurred"}
                        {status === "ABORTED_ON_RISK" && "Aborted - High Risk Detected"}
                    </span>
                </div>
                <RiskBadge level={riskLevel} />
            </div>

            {/* Active Agent Card */}
            {currentAgent && (status === "executing" || status === "planning") && (
                <ActiveAgentCard agentId={currentAgent} />
            )}

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 dark:bg-red-950/30 rounded-xl border border-red-200 dark:border-red-800">
                    <div className="flex items-start gap-3 text-red-700 dark:text-red-400">
                        <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <div className="text-sm">{error}</div>
                    </div>
                </div>
            )}

            {/* Risk Alert for ABORTED_ON_RISK */}
            {status === "ABORTED_ON_RISK" && (
                <div className="p-4 bg-red-50 dark:bg-red-950/30 rounded-xl border border-red-300 dark:border-red-700">
                    <div className="flex items-start gap-3">
                        <Shield className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
                        <div>
                            <div className="font-semibold text-red-800 dark:text-red-200">Risk Advisor Alert</div>
                            <div className="text-sm text-red-700 dark:text-red-300 mt-1">
                                Critical risk detected. The workflow was stopped to protect you. Please review the analysis carefully.
                            </div>
                        </div>
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
        render: ({ state }) => {
            if (!state || state.status === "idle") return null;
            return <AgentStatusDisplay state={state} />;
        },
    });
}

export default AgentStatusDisplay;
