"use client";

import { useChatStore, Conversation } from "@/lib/chat-store";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Plus, MessageSquare, Trash2 } from "lucide-react";
import { useMemo } from "react";

function groupConversationsByDate(conversations: Conversation[]) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    const groups: { label: string; conversations: Conversation[] }[] = [
        { label: "Today", conversations: [] },
        { label: "Yesterday", conversations: [] },
        { label: "Previous 7 Days", conversations: [] },
        { label: "Older", conversations: [] },
    ];

    for (const conv of conversations) {
        const date = new Date(conv.updatedAt);
        if (date >= today) {
            groups[0].conversations.push(conv);
        } else if (date >= yesterday) {
            groups[1].conversations.push(conv);
        } else if (date >= lastWeek) {
            groups[2].conversations.push(conv);
        } else {
            groups[3].conversations.push(conv);
        }
    }

    return groups.filter((g) => g.conversations.length > 0);
}

export function ChatHistorySidebar({ className }: { className?: string }) {
    const {
        conversations,
        currentConversationId,
        addConversation,
        setCurrentConversation,
        deleteConversation,
    } = useChatStore();

    const groupedConversations = useMemo(
        () => groupConversationsByDate(conversations),
        [conversations]
    );

    const handleNewChat = () => {
        addConversation();
    };

    return (
        <div
            className={cn(
                "flex h-full w-64 flex-col border-r bg-sidebar",
                className
            )}
        >
            {/* Header */}
            <div className="flex items-center justify-between border-b p-3">
                <h2 className="text-sm font-semibold text-sidebar-foreground">
                    Chat History
                </h2>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleNewChat}
                    className="h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent"
                >
                    <Plus className="h-4 w-4" />
                </Button>
            </div>

            {/* Conversation List */}
            <ScrollArea className="flex-1 p-2">
                {groupedConversations.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-8 text-center">
                        <MessageSquare className="mb-2 h-8 w-8 text-muted-foreground/50" />
                        <p className="text-xs text-muted-foreground">
                            No conversations yet
                        </p>
                        <Button
                            variant="link"
                            size="sm"
                            onClick={handleNewChat}
                            className="mt-1 text-xs"
                        >
                            Start a new chat
                        </Button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {groupedConversations.map((group) => (
                            <div key={group.label}>
                                <p className="mb-1 px-2 text-xs font-medium text-muted-foreground">
                                    {group.label}
                                </p>
                                <div className="space-y-0.5">
                                    {group.conversations.map((conv) => (
                                        <div
                                            key={conv.id}
                                            className={cn(
                                                "group relative flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors cursor-pointer",
                                                currentConversationId === conv.id
                                                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                                                    : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                                            )}
                                            onClick={() =>
                                                setCurrentConversation(conv.id)
                                            }
                                        >
                                            <MessageSquare className="h-4 w-4 shrink-0 opacity-60" />
                                            <span className="flex-1 truncate">
                                                {conv.title}
                                            </span>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    deleteConversation(conv.id);
                                                }}
                                            >
                                                <Trash2 className="h-3 w-3 text-destructive" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </ScrollArea>

            {/* Footer */}
            <div className="border-t p-3">
                <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start gap-2"
                    onClick={handleNewChat}
                >
                    <Plus className="h-4 w-4" />
                    New Chat
                </Button>
            </div>
        </div>
    );
}
