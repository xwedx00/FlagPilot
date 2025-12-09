"use client";

/**
 * FeedbackButtons - RLHF Thumbs Up/Down
 * =====================================
 * Allows users to rate agent responses.
 * Positive ratings (thumbs up) store in Global Wisdom.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ThumbsUp, ThumbsDown, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { thumbsUp, thumbsDown, submitFeedback } from "@/lib/api";

interface FeedbackButtonsProps {
    messageId: string;
    workflowId?: string;
    agentId?: string;
    className?: string;
    onFeedback?: (rating: number) => void;
}

export function FeedbackButtons({
    messageId,
    workflowId,
    agentId,
    className,
    onFeedback,
}: FeedbackButtonsProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState<"up" | "down" | null>(null);

    const handleFeedback = async (rating: number) => {
        if (submitted) return;

        setIsSubmitting(true);

        try {
            const feedbackWorkflowId = workflowId || messageId;

            if (rating >= 4) {
                await thumbsUp(feedbackWorkflowId);
                setSubmitted("up");
            } else {
                await thumbsDown(feedbackWorkflowId);
                setSubmitted("down");
            }

            onFeedback?.(rating);
        } catch (error) {
            console.error("Failed to submit feedback:", error);
            // Still mark as submitted to prevent spam
            setSubmitted(rating >= 4 ? "up" : "down");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <div className={cn("flex items-center gap-1 text-xs text-muted-foreground", className)}>
                <Check className="h-3 w-3 text-green-500" />
                <span>Thanks for your feedback!</span>
            </div>
        );
    }

    return (
        <div className={cn("flex items-center gap-1", className)}>
            <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-muted-foreground hover:text-green-500"
                onClick={() => handleFeedback(5)}
                disabled={isSubmitting}
                title="Good response - helps improve AI"
            >
                {isSubmitting ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                    <ThumbsUp className="h-3.5 w-3.5" />
                )}
            </Button>
            <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-muted-foreground hover:text-red-500"
                onClick={() => handleFeedback(1)}
                disabled={isSubmitting}
                title="Poor response"
            >
                <ThumbsDown className="h-3.5 w-3.5" />
            </Button>
        </div>
    );
}

// Inline version for chat messages
export function InlineFeedback({
    messageId,
    workflowId,
    className,
}: {
    messageId: string;
    workflowId?: string;
    className?: string;
}) {
    return (
        <div className={cn("opacity-0 group-hover:opacity-100 transition-opacity", className)}>
            <FeedbackButtons messageId={messageId} workflowId={workflowId} />
        </div>
    );
}
