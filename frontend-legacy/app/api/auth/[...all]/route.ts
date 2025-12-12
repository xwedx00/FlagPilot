import { auth } from "@/lib/auth"; // path to your auth file
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest, NextResponse } from "next/server";

const handler = toNextJsHandler(auth);

// Add CORS headers for browser preview proxy
function addCorsHeaders(response: NextResponse, origin: string | null) {
  if (origin) {
    response.headers.set("Access-Control-Allow-Origin", origin);
    response.headers.set("Access-Control-Allow-Credentials", "true");
    response.headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    response.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  }
  return response;
}

// Handle preflight OPTIONS requests
export async function OPTIONS(request: NextRequest) {
  const origin = request.headers.get("origin");
  const response = new NextResponse(null, { status: 200 });
  return addCorsHeaders(response, origin);
}

export async function GET(request: NextRequest) {
  const origin = request.headers.get("origin");
  try {
    const response = await handler.GET(request);
    // Clone and add CORS headers
    const newResponse = new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
    return addCorsHeaders(newResponse, origin);
  } catch (error) {
    console.error("[Auth GET Error]:", error);
    const errorResponse = NextResponse.json(
      { error: "Authentication error", details: String(error) },
      { status: 500 }
    );
    return addCorsHeaders(errorResponse, origin);
  }
}

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  try {
    const response = await handler.POST(request);
    // Clone and add CORS headers
    const newResponse = new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
    return addCorsHeaders(newResponse, origin);
  } catch (error) {
    console.error("[Auth POST Error]:", error);
    const errorResponse = NextResponse.json(
      { error: "Authentication error", details: String(error) },
      { status: 500 }
    );
    return addCorsHeaders(errorResponse, origin);
  }
}
