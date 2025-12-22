"use client";

import { useCopilotChat } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
// import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";

import { Send, User, Bot, AlertTriangle, Shield, CheckCircle, Loader2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { authClient } from "@/lib/auth-client";

// FlagPilot CopilotKit integrations
import { useFlagPilotActions } from "@/lib/hooks/use-flagpilot-actions";
import { useAgentStatusRenderer, AgentStatusDisplay } from "@/components/chat/agent-status";


export function ChatInterface() {
    // 1. Get Session for Auth Headers
    const { data: session } = authClient.useSession();

    // 2. Pass headers to useCopilotChat
    const { visibleMessages, appendMessage, isLoading } = useCopilotChat({
        headers: session?.user?.id ? {
            "Authorization": `Bearer ${session.user.id}`
        } : {}
    });

    // 3. FlagPilot CopilotKit Actions (registers 6 actions with AI)
    const { agentState } = useFlagPilotActions();

    // 4. Agent Status Renderer (shows agent progress in chat)
    useAgentStatusRenderer();

    const messages = visibleMessages || [];
    console.log("Render: messages count:", messages.length);

    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    // Connectivity Test
    useEffect(() => {
        console.log("Testing connectivity to backend...");
        fetch("/api/health")
            .then(res => res.text())
            .then(txt => console.log("Health Check Result:", txt))
            .catch(err => console.error("Health Check Failed:", err));
    }, []);

    // In handleSend
    const handleSend = async () => {
        console.log("handleSend called with input:", input);
        if (!input.trim()) return;

        try {
            // Duck-typing the message to bypass instanceof checks between packages
            const msg: any = {
                id: crypto.randomUUID(),
                role: "user",
                content: input,
                createdAt: new Date(),
                isTextMessage: () => true,
                isActionExecutionMessage: () => false,
                isResultMessage: () => false,
            };
            console.log("Appending message (duck-typed):", msg);
            await appendMessage(msg);
            console.log("Message appended successfully");
        } catch (e) {
            console.error("Failed to append message:", e);
        }

        setInput("");
    };



    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto w-full bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-sm overflow-hidden mt-4">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-zinc-100 dark:border-zinc-800 bg-white dark:bg-zinc-950">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md">
                            <Bot className="w-6 h-6" />
                        </div>
                        {isLoading && (
                            <span className="absolute -bottom-1 -right-1 flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                            </span>
                        )}
                    </div>
                    <div>
                        <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">FlagPilot Orchestrator</h2>
                        <p className="text-xs text-zinc-500 flex items-center gap-1">
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-3 h-3 animate-spin" /> Processing...
                                </>
                            ) : (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" /> Active & Ready
                                </>
                            )}
                        </p>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4 bg-zinc-50/50 dark:bg-zinc-900/50">
                <div className="space-y-6">
                    {/* Agent Status Display - Shows real-time agent progress */}
                    {agentState.status !== "idle" && (
                        <AgentStatusDisplay state={agentState} />
                    )}

                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4 opacity-50">
                            <Shield className="w-16 h-16 text-zinc-300" />
                            <div>
                                <h3 className="text-lg font-medium text-zinc-700">FlagPilot Protection System</h3>
                                <p className="text-sm text-zinc-500 max-w-xs mx-auto">Paste a job offer, contract, or client message to begin analysis.</p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg: any, idx) => (
                        <div
                            key={msg.id || idx}
                            className={`flex items-start gap-3 ${String(msg.role).toLowerCase() === "user" ? "flex-row-reverse" : ""
                                }`}
                        >
                            <Avatar className={`w-8 h-8 ${String(msg.role).toLowerCase() === "user" ? "bg-zinc-200" : "bg-indigo-100"}`}>
                                <AvatarFallback>
                                    {String(msg.role).toLowerCase() === "user" ? <User className="w-4 h-4 text-zinc-600" /> : <Bot className="w-4 h-4 text-indigo-600" />}
                                </AvatarFallback>
                            </Avatar>

                            <div className={`flex flex-col gap-1 max-w-[80%] ${String(msg.role).toLowerCase() === "user" ? "items-end" : "items-start"}`}>
                                <div
                                    className={`px-4 py-3 rounded-2xl shadow-sm text-sm whitespace-pre-wrap leading-relaxed ${String(msg.role).toLowerCase() === "user"
                                        ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 rounded-tr-none"
                                        : "bg-white border border-zinc-200 text-zinc-800 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 rounded-tl-none"
                                        }`}
                                >
                                    {msg.content}
                                </div>
                                {/* Timestamp or status could go here */}
                            </div>
                        </div>
                    ))}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-zinc-950 border-t border-zinc-100 dark:border-zinc-800">
                <div className="relative flex items-end gap-2 p-1.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-900 focus-within:ring-2 focus-within:ring-indigo-100 dark:focus-within:ring-indigo-900 transition-all">
                    <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Describe your situation or paste a contract..."
                        className="border-0 focus-visible:ring-0 bg-transparent resize-none min-h-[50px] max-h-[200px] py-3 text-sm"
                    />
                    <Button
                        disabled={!input.trim() || isLoading}
                        onClick={handleSend}
                        size="icon"
                        className="mb-1 h-9 w-9 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-colors"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </Button>
                </div>
                <div className="text-[10px] text-zinc-400 text-center mt-2 flex items-center justify-center gap-1">
                    <LockIcon className="w-3 h-3" /> Encrypted & Secure
                </div>
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
