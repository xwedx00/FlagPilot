"use client";

import { useState, useEffect } from "react";
import { Brain, MessageSquare, Lightbulb, History, User, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Memory Panel Types
 */
interface UserProfile {
    userId: string;
    summary: string;
    preferences: Record<string, any>;
    riskTolerance?: string;
    lastUpdated?: string;
}

interface ChatSession {
    sessionId: string;
    timestamp: string;
    messageCount: number;
    preview: string;
}

interface WisdomInsight {
    category: string;
    insight: string;
    confidenceScore: number;
    sourceCount: number;
}

interface MemoryPanelProps {
    userId?: string;
    isOpen?: boolean;
    onToggle?: () => void;
    className?: string;
}

/**
 * Collapsible Section Component
 */
function CollapsibleSection({
    title,
    icon: Icon,
    children,
    defaultOpen = false,
}: {
    title: string;
    icon: any;
    children: React.ReactNode;
    defaultOpen?: boolean;
}) {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className="border-b border-zinc-200 dark:border-zinc-700 last:border-b-0">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
            >
                <div className="flex items-center gap-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    <Icon className="w-4 h-4 text-indigo-500" />
                    {title}
                </div>
                {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-zinc-400" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-zinc-400" />
                )}
            </button>
            {isOpen && (
                <div className="px-4 pb-4">
                    {children}
                </div>
            )}
        </div>
    );
}

/**
 * User Profile Card
 */
function ProfileCard({ profile }: { profile: UserProfile | null }) {
    if (!profile || !profile.summary) {
        return (
            <div className="text-sm text-zinc-500 dark:text-zinc-400 italic">
                No profile yet. As you interact, FlagPilot learns your preferences.
            </div>
        );
    }

    return (
        <div className="space-y-2">
            <div className="text-sm text-zinc-600 dark:text-zinc-300 whitespace-pre-wrap">
                {profile.summary.slice(0, 200)}
                {profile.summary.length > 200 && "..."}
            </div>
            {profile.riskTolerance && (
                <div className="flex items-center gap-2 text-xs">
                    <span className="text-zinc-500">Risk Tolerance:</span>
                    <span className={cn(
                        "px-2 py-0.5 rounded-full font-medium",
                        profile.riskTolerance === "low" && "bg-green-100 text-green-700",
                        profile.riskTolerance === "medium" && "bg-yellow-100 text-yellow-700",
                        profile.riskTolerance === "high" && "bg-red-100 text-red-700",
                    )}>
                        {profile.riskTolerance}
                    </span>
                </div>
            )}
        </div>
    );
}

/**
 * Recent Sessions List
 */
function SessionsList({ sessions }: { sessions: ChatSession[] }) {
    if (!sessions || sessions.length === 0) {
        return (
            <div className="text-sm text-zinc-500 dark:text-zinc-400 italic">
                No previous sessions.
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {sessions.slice(0, 5).map((session) => (
                <div
                    key={session.sessionId}
                    className="p-2 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                    <div className="text-sm font-medium text-zinc-700 dark:text-zinc-300 truncate">
                        {session.preview}
                    </div>
                    <div className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-2 mt-1">
                        <span>{new Date(session.timestamp).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{session.messageCount} messages</span>
                    </div>
                </div>
            ))}
        </div>
    );
}

/**
 * Wisdom Insights List
 */
function WisdomList({ insights }: { insights: WisdomInsight[] }) {
    if (!insights || insights.length === 0) {
        return (
            <div className="text-sm text-zinc-500 dark:text-zinc-400 italic">
                No wisdom tips available yet.
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {insights.slice(0, 5).map((insight, idx) => (
                <div
                    key={idx}
                    className="p-3 rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-800/50"
                >
                    <div className="flex items-start gap-2">
                        <Sparkles className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <div className="text-sm text-amber-900 dark:text-amber-100">
                                {insight.insight}
                            </div>
                            <div className="text-xs text-amber-600 dark:text-amber-400 mt-1 flex items-center gap-2">
                                <span className="capitalize">{insight.category}</span>
                                <span>•</span>
                                <span>{Math.round(insight.confidenceScore * 100)}% confidence</span>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

/**
 * Memory Panel Component
 * Shows user profile, chat history, and global wisdom
 */
export function MemoryPanel({ userId, isOpen = true, onToggle, className }: MemoryPanelProps) {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [wisdom, setWisdom] = useState<WisdomInsight[]>([]);
    const [loading, setLoading] = useState(false);

    // Placeholder data for demo - in production this would fetch from backend
    useEffect(() => {
        // Simulated data - replace with actual API calls
        setWisdom([
            {
                category: "contracts",
                insight: "Always get a deposit before starting work - 30-50% upfront is standard.",
                confidenceScore: 0.95,
                sourceCount: 847,
            },
            {
                category: "negotiation",
                insight: "Anchor high in negotiations - your first number sets the range.",
                confidenceScore: 0.88,
                sourceCount: 523,
            },
            {
                category: "scams",
                insight: "Be wary of clients who want to move communication off-platform immediately.",
                confidenceScore: 0.92,
                sourceCount: 1204,
            },
        ]);
    }, [userId]);

    if (!isOpen) return null;

    return (
        <div className={cn(
            "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-xl shadow-sm overflow-hidden",
            className
        )}>
            {/* Header */}
            <div className="px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-between">
                <div className="flex items-center gap-2 text-white font-semibold">
                    <Brain className="w-5 h-5" />
                    FlagPilot Memory
                </div>
                {onToggle && (
                    <button onClick={onToggle} className="text-white/80 hover:text-white">
                        <ChevronUp className="w-4 h-4" />
                    </button>
                )}
            </div>

            {/* Content */}
            <div className="divide-y divide-zinc-200 dark:divide-zinc-700">
                <CollapsibleSection title="Your Profile" icon={User} defaultOpen={true}>
                    <ProfileCard profile={profile} />
                </CollapsibleSection>

                <CollapsibleSection title="Recent Sessions" icon={History}>
                    <SessionsList sessions={sessions} />
                </CollapsibleSection>

                <CollapsibleSection title="Global Wisdom" icon={Lightbulb} defaultOpen={true}>
                    <WisdomList insights={wisdom} />
                </CollapsibleSection>
            </div>
        </div>
    );
}

export default MemoryPanel;
