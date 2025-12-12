/**
 * Chat API Route - Proxies to Backend MetaGPT
 * ============================================
 * ALL LLM calls go through the backend MetaGPT agents.
 * This route proxies requests to the backend /api/v1/stream/chat endpoint.
 */

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

// Extract text content from any message format
function extractText(msg: any): string {
  if (!msg) return "";

  // Handle parts array (AI SDK 6 format)
  if (msg.parts && Array.isArray(msg.parts)) {
    return msg.parts
      .filter((p: any) => p.type === "text" && p.text)
      .map((p: any) => p.text)
      .join("");
  }
  // Handle string content
  if (typeof msg.content === "string") {
    return msg.content;
  }
  // Handle content array
  if (Array.isArray(msg.content)) {
    return msg.content
      .filter((p: any) => p.type === "text")
      .map((p: any) => p.text || "")
      .join("");
  }
  return "";
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const messages: any[] = body.messages || [];

    // Get the latest user message
    const userMessages = messages.filter((m: any) => m.role === "user");
    if (userMessages.length === 0) {
      return new Response(
        JSON.stringify({ error: "No user message provided" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const latestMessage = extractText(userMessages[userMessages.length - 1]);
    if (!latestMessage) {
      return new Response(
        JSON.stringify({ error: "Empty message" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Build conversation context from previous messages
    const context: { previousMessages?: Array<{ role: string; content: string }> } = {};
    if (messages.length > 1) {
      context.previousMessages = messages.slice(0, -1).map((m: any) => ({
        role: m.role,
        content: extractText(m),
      })).filter((m: { content: string }) => m.content.length > 0);
    }

    // Proxy to backend MetaGPT endpoint
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/v1/stream/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: latestMessage,
        context: context,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error("Backend error:", error);
      return new Response(
        JSON.stringify({ error: "Backend service error" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Stream the response from backend
    // Backend uses Vercel AI Data Stream format
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              if (!line.trim()) continue;

              // Parse Vercel AI Data Stream format
              // Format: "0:text" for text chunks
              const match = line.match(/^(\d+):(.*)$/);
              if (match) {
                const [, type, content] = match;
                if (type === "0") {
                  // Text content - parse JSON string
                  try {
                    const text = JSON.parse(content);
                    if (text) {
                      controller.enqueue(encoder.encode(text));
                    }
                  } catch {
                    // If not JSON, send as-is
                    controller.enqueue(encoder.encode(content));
                  }
                }
                // Types 2, 8, d are metadata/status - skip for plain text output
              }
            }
          }
        } finally {
          reader.releaseLock();
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to process chat request" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
