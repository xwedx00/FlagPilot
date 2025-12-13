"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

export interface Conversation {
    id: string;
    title: string;
    createdAt: Date;
    updatedAt: Date;
}

interface ChatStore {
    conversations: Conversation[];
    currentConversationId: string | null;
    addConversation: (title?: string) => string;
    setCurrentConversation: (id: string | null) => void;
    deleteConversation: (id: string) => void;
    renameConversation: (id: string, title: string) => void;
    getCurrentConversation: () => Conversation | null;
}

const ChatStoreContext = createContext<ChatStore | null>(null);

export function ChatStoreProvider({ children }: { children: ReactNode }) {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

    const addConversation = useCallback((title?: string) => {
        const id = `conv-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        const now = new Date();
        const newConversation: Conversation = {
            id,
            title: title || "New Chat",
            createdAt: now,
            updatedAt: now,
        };
        setConversations((prev) => [newConversation, ...prev]);
        setCurrentConversationId(id);
        return id;
    }, []);

    const setCurrentConversation = useCallback((id: string | null) => {
        setCurrentConversationId(id);
    }, []);

    const deleteConversation = useCallback((id: string) => {
        setConversations((prev) => prev.filter((c) => c.id !== id));
        if (currentConversationId === id) {
            setCurrentConversationId(null);
        }
    }, [currentConversationId]);

    const renameConversation = useCallback((id: string, title: string) => {
        setConversations((prev) =>
            prev.map((c) =>
                c.id === id ? { ...c, title, updatedAt: new Date() } : c
            )
        );
    }, []);

    const getCurrentConversation = useCallback(() => {
        return conversations.find((c) => c.id === currentConversationId) || null;
    }, [conversations, currentConversationId]);

    return (
        <ChatStoreContext.Provider
            value={{
                conversations,
                currentConversationId,
                addConversation,
                setCurrentConversation,
                deleteConversation,
                renameConversation,
                getCurrentConversation,
            }}
        >
            {children}
        </ChatStoreContext.Provider>
    );
}

export function useChatStore() {
    const context = useContext(ChatStoreContext);
    if (!context) {
        throw new Error("useChatStore must be used within a ChatStoreProvider");
    }
    return context;
}
