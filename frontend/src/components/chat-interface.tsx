"use client";

import { useChat } from "@ai-sdk/react";
import { Send, Square, Flag } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

import {
    ChatContainerRoot,
    ChatContainerContent,
    ChatContainerScrollAnchor,
} from "@/components/ui/chat-container";
import {
    PromptInput,
    PromptInputTextarea,
    PromptInputActions,
    PromptInputAction,
} from "@/components/ui/prompt-input";
import {
    Message,
    MessageContent,
    MessageAvatar,
} from "@/components/ui/message";
import { ScrollButton } from "@/components/ui/scroll-button";
import { Loader } from "@/components/ui/loader";
import { Button } from "@/components/ui/button";
import { PromptSuggestion } from "@/components/ui/prompt-suggestion";
import { ChatUpload } from "@/components/chat-upload";

// Helper to extract text content from AI SDK v6 message parts
function getMessageText(message: any): string {
    console.log("getMessageText called with:", message);

    if (message.parts && Array.isArray(message.parts)) {
        const text = message.parts
            .filter((part: any) => part.type === 'text')
            .map((part: any) => part.text || '')
            .join('');
        console.log("Extracted from parts:", text);
        return text;
    }
    if (typeof message.content === 'string') {
        console.log("Using content string:", message.content);
        return message.content;
    }
    console.log("No text found");
    return '';
}

const SUGGESTIONS = [
    "Review my freelance contract for red flags",
    "Help me write a project proposal",
    "What's a fair rate for my skills?",
    "Draft a follow-up email to a client",
];

export function ChatInterface() {
    const [input, setInput] = useState("");

    const {
        messages,
        sendMessage,
        stop,
        status,
        error,
    } = useChat({
        // The backend uses Vercel AI SDK Data Stream Protocol v1
        // which sends text/plain with code prefixes (0: for text, 2: for data, d: for finish)
        onError: (err) => {
            console.error("Chat error:", err);
            toast.error("Failed to send message");
        },
        onFinish: (message) => {
            console.log("Chat finished:", message);
        },
    });

    const isLoading = status === "streaming" || status === "submitted";

    useEffect(() => {
        console.log("Chat Debug:", { status, isLoading, messageCount: messages.length, error });
        if (messages.length > 0) {
            console.log("Messages:", JSON.stringify(messages, null, 2));
        }
    }, [status, isLoading, messages, error]);

    const handleSubmit = async () => {
        if (!input.trim() || isLoading) return;

        const text = input;
        setInput("");

        try {
            await sendMessage({
                role: "user",
                content: text,
            } as any);
        } catch (err) {
            console.error("Send failed:", err);
            setInput(text);
            toast.error("Failed to send message");
        }
    };

    const handleSuggestionClick = async (suggestion: string) => {
        if (isLoading) return;
        try {
            await sendMessage({
                role: "user",
                content: suggestion,
            } as any);
        } catch (err) {
            console.error("Send failed:", err);
        }
    };

    const hasMessages = messages.length > 0;

    return (
        <div className="flex flex-col h-[600px] min-h-[400px] rounded-xl border bg-card shadow-sm">
            {/* Chat Messages Area */}
            <div className="flex-1 overflow-hidden relative">
                <ChatContainerRoot className="h-full">
                    <ChatContainerContent className="p-4 gap-4">
                        {/* Empty State */}
                        {!hasMessages && !isLoading && (
                            <div className="flex flex-col items-center justify-center min-h-[300px] py-8">
                                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary">
                                    <Flag className="h-7 w-7 text-primary-foreground" />
                                </div>
                                <h2 className="mb-2 text-xl font-semibold text-foreground">
                                    How can I help you today?
                                </h2>
                                <p className="mb-6 max-w-md text-center text-sm text-muted-foreground">
                                    Ask me anything about freelancing, contracts, proposals, or client communication.
                                </p>

                                {/* Prompt Suggestions */}
                                <div className="flex flex-wrap justify-center gap-2 max-w-xl px-4">
                                    {SUGGESTIONS.map((suggestion, idx) => (
                                        <PromptSuggestion
                                            key={idx}
                                            onClick={() => handleSuggestionClick(suggestion)}
                                        >
                                            {suggestion}
                                        </PromptSuggestion>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Messages */}
                        {messages.map((message) => {
                            const isUser = message.role === "user";
                            const text = getMessageText(message);

                            console.log("Rendering message:", message.id, "text:", text?.slice(0, 50));

                            if (!text) return null;

                            return (
                                <Message key={message.id}>
                                    <MessageAvatar
                                        fallback={isUser ? "U" : "AI"}
                                        alt={isUser ? "User" : "AI Assistant"}
                                        className={isUser ? "bg-secondary" : "bg-primary text-primary-foreground"}
                                    />
                                    <MessageContent
                                        markdown={!isUser}
                                        id={message.id}
                                        className={cn(
                                            "max-w-[80%]",
                                            isUser
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-secondary text-secondary-foreground prose-invert dark:prose-invert"
                                        )}
                                    >
                                        {text}
                                    </MessageContent>
                                </Message>
                            );
                        })}

                        {/* Loading State */}
                        {isLoading && (
                            <Message>
                                <MessageAvatar
                                    fallback="AI"
                                    alt="AI Assistant"
                                    className="bg-primary text-primary-foreground"
                                />
                                <div className="flex items-center gap-2 rounded-lg bg-secondary p-3">
                                    <Loader variant="typing" size="sm" />
                                    <span className="text-sm text-muted-foreground">
                                        Thinking...
                                    </span>
                                </div>
                            </Message>
                        )}

                        {/* Error State */}
                        {error && (
                            <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
                                <p className="text-sm font-medium">Error: {error.message}</p>
                            </div>
                        )}
                    </ChatContainerContent>
                    <ChatContainerScrollAnchor />

                    {/* Scroll to bottom button - must be inside ChatContainerRoot for context */}
                    <div className="absolute bottom-4 right-4 z-10">
                        <ScrollButton />
                    </div>
                </ChatContainerRoot>
            </div>


            {/* Input Area */}
            <div className="border-t p-4 bg-card shrink-0">
                <PromptInput
                    value={input}
                    onValueChange={setInput}
                    isLoading={isLoading}
                    onSubmit={handleSubmit}
                    className="bg-background border"
                >
                    <PromptInputTextarea
                        placeholder="Ask anything..."
                        className="min-h-[44px]"
                    />
                    <PromptInputActions>
                        <PromptInputAction tooltip="Attach file">
                            <ChatUpload
                                onUpload={(name) => toast.success(`Added: ${name}`)}
                            />
                        </PromptInputAction>

                        {isLoading ? (
                            <Button
                                type="button"
                                variant="destructive"
                                size="icon"
                                className="h-8 w-8 rounded-full"
                                onClick={() => stop()}
                            >
                                <Square className="h-4 w-4" />
                            </Button>
                        ) : (
                            <Button
                                type="button"
                                size="icon"
                                className="h-8 w-8 rounded-full"
                                disabled={!input.trim()}
                                onClick={handleSubmit}
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        )}
                    </PromptInputActions>
                </PromptInput>
                <p className="mt-2 text-center text-xs text-muted-foreground">
                    FlagPilot can make mistakes. Verify important information.
                </p>
            </div>
        </div>
    );
}
