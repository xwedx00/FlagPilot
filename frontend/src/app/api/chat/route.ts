
import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { messages, userId } = body;

        // Get the last user message
        const lastMessage = messages[messages.length - 1];
        const userMessage = lastMessage.content;

        // Backend URL (Internal Docker Network or Localhost)
        // Since this runs on the server (Next.js), if in Docker, use service name.
        // If running with `pnpm dev` on host, use localhost.
        // We'll assume localhost:8000 for now as verified in previous steps.
        const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

        // Call Backend
        const response = await fetch(`${backendUrl}/api/v1/stream/workflow`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: userMessage,
                user_id: userId || "anonymous",
                // Pass history as context if needed, but for now just the prompt.
                context: {}
            }),
        });

        if (!response.ok) {
            console.error("Backend Error:", response.status, await response.text());
            return NextResponse.json({ error: "Backend failed" }, { status: 500 });
        }

        // Pipe the stream directly, forwarding AI SDK v6 headers
        const aiStreamHeader = response.headers.get("X-Vercel-AI-UI-Message-Stream");

        return new Response(response.body, {
            headers: {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                ...(aiStreamHeader && { "X-Vercel-AI-UI-Message-Stream": aiStreamHeader }),
            },
        });

    } catch (error) {
        console.error("Chat Proxy Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
