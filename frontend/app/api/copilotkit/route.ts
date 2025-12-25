import {
    CopilotRuntime,
    ExperimentalEmptyAdapter,
    copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";
import { NextRequest } from "next/server";

/**
 * CopilotKit API Route
 * ====================
 * Connects to the FlagPilot backend which hosts the LangGraph agent.
 * 
 * Architecture:
 * - Frontend: CopilotRuntime with LangGraphHttpAgent pointing to backend
 * - Backend: FastAPI with CopilotKit SDK exposing the flagpilot_orchestrator agent
 * 
 * Pattern from: https://github.com/CopilotKit/with-langgraph-fastapi
 */

// Use ExperimentalEmptyAdapter since the backend handles all LLM calls
const serviceAdapter = new ExperimentalEmptyAdapter();

// Backend URL for the CopilotKit agent endpoint
const BACKEND_URL = process.env.BACKEND_COPILOT_URL || "http://127.0.0.1:8000/copilotkit";

// Create the CopilotRuntime with LangGraphHttpAgent for AG-UI integration
const runtime = new CopilotRuntime({
    agents: {
        flagpilot_orchestrator: new LangGraphHttpAgent({
            url: BACKEND_URL,
        }),
    },
});

export const POST = async (req: NextRequest) => {
    try {
        const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
            runtime,
            serviceAdapter,
            endpoint: "/api/copilotkit",
        });

        return await handleRequest(req);
    } catch (err: unknown) {
        const error = err as Error;
        console.error("[CopilotKit] Runtime Error:", error.message);
        return new Response(
            JSON.stringify({ error: error.message }),
            { status: 500, headers: { "Content-Type": "application/json" } }
        );
    }
};
