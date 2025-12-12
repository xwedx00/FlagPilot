import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    // Get session
    const session = await auth.api.getSession({
      headers: await headers(),
    })
    
    if (!session?.user) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      )
    }
    
    const body = await request.json()
    const { filename, contentType, projectId } = body
    
    if (!filename) {
      return NextResponse.json(
        { error: "Filename is required" },
        { status: 400 }
      )
    }
    
    // Forward to Python backend
    const response = await fetch(`${BACKEND_URL}/api/v1/files/upload-url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Forward auth cookie
        "Cookie": request.headers.get("cookie") || "",
      },
      body: JSON.stringify({
        filename,
        content_type: contentType || "application/octet-stream",
        project_id: projectId,
      }),
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error("Backend error:", errorText)
      return NextResponse.json(
        { error: "Failed to get upload URL" },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    
    return NextResponse.json({
      uploadUrl: data.upload_url,
      objectKey: data.object_key,
      fileId: data.file_id,
      bucket: data.bucket,
      expiresIn: data.expires_in_seconds,
    })
    
  } catch (error) {
    console.error("Upload URL error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}
