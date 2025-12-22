import { CopilotRuntime, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const runtime = new CopilotRuntime({
    remoteEndpoints: [
        {
            url: process.env.BACKEND_COPILOT_URL || "http://localhost:8000/copilotkit",
        }
    ],
});

export const POST = async (req: NextRequest) => {
    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
        runtime,
        endpoint: "/api/copilotkit",
    });
    return handleRequest(req);
};
