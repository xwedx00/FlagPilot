"use client";

import React from "react";
import { useCoAgent, useCoAgentStateRender } from "@copilotkit/react-core";
import { AgentStatusDisplay } from "@/components/chat/agent-status";

/**
 * FlagPilot Shared State Hook
 * ===========================
 * Bidirectional state sharing between frontend and backend LangGraph agent.
 * Uses CopilotKit's useCoAgent for real-time state synchronization.
 */

// State schema matching backend FlagPilotState in graph.py
export interface FlagPilotState {
    // Task information
    task: string;
    context: Record<string, any>;

    // Execution state
    status: "idle" | "planning" | "executing" | "complete" | "error" | "COMPLETED" | "ABORTED_ON_RISK";
    currentAgent: string | null;
    agentOutputs: Record<string, string>;

    // Results
    orchestratorAnalysis: Record<string, any> | null;
    finalSynthesis: string | null;
    riskLevel: "none" | "low" | "medium" | "high" | "critical";

    // Error handling
    error: string | null;

    // Memory integration
    userProfile?: {
        userId: string;
        summary: string;
        preferences: Record<string, any>;
    };
    chatHistory?: Array<{
        role: string;
        content: string;
        timestamp: string;
    }>;
}

// Initial state
const initialState: FlagPilotState = {
    task: "",
    context: {},
    status: "idle",
    currentAgent: null,
    agentOutputs: {},
    orchestratorAnalysis: null,
    finalSynthesis: null,
    riskLevel: "none",
    error: null,
};

/**
 * Hook to access and modify FlagPilot agent state
 * State is synchronized bidirectionally with the backend LangGraph agent
 */
export function useFlagPilotState() {
    const {
        name,
        nodeName,
        state,
        setState,
        running,
        start,
        stop,
        run,
    } = useCoAgent<FlagPilotState>({
        name: "flagpilot_orchestrator",
        initialState,
    });

    // Derived helpers
    const isProcessing = running || state?.status === "executing" || state?.status === "planning";
    const hasError = state?.status === "error" || !!state?.error;
    const isComplete = state?.status === "complete" || state?.status === "COMPLETED";
    const isHighRisk = state?.riskLevel === "high" || state?.riskLevel === "critical";

    // Reset state helper
    const resetState = () => {
        setState(initialState);
    };

    // Update specific fields - using state directly since CopilotKit setState may not support updater functions
    const updateContext = (newContext: Record<string, any>) => {
        if (state) {
            setState({
                ...state,
                context: { ...state.context, ...newContext }
            });
        }
    };

    return {
        // Core state
        state,
        setState,
        nodeName,

        // Running state
        running,
        isProcessing,
        hasError,
        isComplete,
        isHighRisk,

        // Agent control
        start,
        stop,
        run,
        resetState,

        // Helpers
        updateContext,
        currentAgent: state?.currentAgent,
        riskLevel: state?.riskLevel || "none",
        finalSynthesis: state?.finalSynthesis,
        agentOutputs: state?.agentOutputs || {},
    };
}

/**
 * Hook to render agent state in chat using Generative UI
 * Automatically renders AgentStatusDisplay for active agents
 */
export function useFlagPilotStateRenderer() {
    useCoAgentStateRender<FlagPilotState>({
        name: "flagpilot_orchestrator",
        render: ({ status, state, nodeName }) => {
            // Don't render for idle state
            if (!state || state.status === "idle") return null;

            // Map to component-expected format
            const displayState = {
                status: state.status as any,
                currentAgent: state.currentAgent,
                riskLevel: state.riskLevel,
                error: state.error || undefined,
            };

            return <AgentStatusDisplay state={displayState} />;
        },
    });
}

export default useFlagPilotState;
