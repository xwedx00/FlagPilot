"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotChat } from "@copilotkit/react-core";
import { Role, TextMessage } from "@copilotkit/runtime-client-gql";
import { Send, User, Bot, Shield, Loader2, Brain, MessageSquare } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Metadata } from "next";

// FlagPilot CopilotKit integrations
import { useFlagPilotActions } from "@/lib/hooks/use-flagpilot-actions";
import { useFlagPilotState, useFlagPilotStateRenderer } from "@/lib/hooks/use-flagpilot-state";
import { AgentStatusDisplay } from "@/components/chat/agent-status";
import { MemoryPanel } from "@/components/chat/memory-panel";

/**
 * ChatInterface Component
 * =======================
 * Uses CopilotKit's built-in CopilotChat for reliable message handling
 * with custom styling and FlagPilot branding.
 */
export function ChatInterface() {
    // Memory panel toggle
    const [showMemory, setShowMemory] = useState(false);

    // FlagPilot state hooks
    const { agentState } = useFlagPilotActions();
    const { state: coAgentState, isProcessing } = useFlagPilotState();
    useFlagPilotStateRenderer();

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto w-full bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-sm overflow-hidden mt-4">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-zinc-100 dark:border-zinc-800 bg-white dark:bg-zinc-950">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md">
                            <Bot className="w-6 h-6" />
                        </div>
                        {isProcessing && (
                            <span className="absolute -bottom-1 -right-1 flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                            </span>
                        )}
                    </div>
                    <div>
                        <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">FlagPilot Orchestrator</h2>
                        <p className="text-xs text-zinc-500 flex items-center gap-1">
                            {isProcessing ? (
                                <>
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                    {coAgentState?.currentAgent ? `${coAgentState.currentAgent} working...` : "Processing..."}
                                </>
                            ) : (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" /> 17 Agents Ready
                                </>
                            )}
                        </p>
                    </div>
                </div>
                {/* Memory Panel Toggle */}
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowMemory(!showMemory)}
                    className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                    <Brain className="w-4 h-4" />
                    <span className="hidden sm:inline">Memory</span>
                </Button>
            </div>

            {/* Memory Panel (Collapsible) */}
            {showMemory && (
                <div className="px-4 py-3 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                    <MemoryPanel
                        isOpen={showMemory}
                        onToggle={() => setShowMemory(false)}
                        className="max-h-[300px] overflow-y-auto"
                    />
                </div>
            )}

            {/* Agent Status Display */}
            {agentState.status !== "idle" && (
                <div className="px-4 py-2 border-b border-zinc-100 dark:border-zinc-800">
                    <AgentStatusDisplay state={agentState} />
                </div>
            )}

            {/* Chat Area - Using CopilotChat for reliable message handling */}
            <div className="flex-1 overflow-hidden">
                <CopilotChat
                    instructions="You are FlagPilot, an AI assistant helping freelancers protect themselves from unfair contracts, scam job postings, and problematic clients. When analyzing contracts, look for unfair terms, IP issues, payment risks, and liability concerns. When checking job postings, identify red flags and scam signals. Be thorough but concise."
                    labels={{
                        title: "",
                        initial: "Paste a job offer, contract, or client message to begin analysis.",
                        placeholder: "Describe your situation or paste a contract..."
                    }}
                    className="h-full [&_.copilotKitHeader]:hidden [&_.copilotKitFooter]:hidden"
                />
            </div>

            {/* Footer */}
            <div className="text-[10px] text-zinc-400 text-center py-2 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-center gap-1 bg-white dark:bg-zinc-950">
                <LockIcon className="w-3 h-3" /> Encrypted & Secure • Powered by FlagPilot AI
            </div>
        </div>
    );
}

function LockIcon({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
    )
}
