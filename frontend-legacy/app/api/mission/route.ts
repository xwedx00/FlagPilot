import { NextRequest } from 'next/server';

// Allow streaming responses up to 60 seconds
export const maxDuration = 60;

// POST /api/mission - Start a new mission
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { title, description, context } = body;

    // Generate mission ID
    const missionId = `mission-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    // In production, this would:
    // 1. Create mission record in database
    // 2. Initialize agent orchestration
    // 3. Return mission ID for SSE subscription

    return Response.json({
      success: true,
      mission: {
        id: missionId,
        title: title || 'New Mission',
        status: 'active',
        createdAt: new Date().toISOString(),
      },
    });
  } catch (error) {
    console.error('Mission creation error:', error);
    return Response.json(
      { error: 'Failed to create mission' },
      { status: 500 }
    );
  }
}

// GET /api/mission - List user's missions
export async function GET() {
  // In production, fetch from database
  return Response.json({
    missions: [],
  });
}
