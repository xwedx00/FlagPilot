import { NextRequest } from 'next/server';

// Allow streaming responses up to 5 minutes for long-running missions
export const maxDuration = 300;

// Backend URL for agent orchestration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// SSE Stream endpoint for real-time mission updates
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: missionId } = await params;
  const searchParams = req.nextUrl.searchParams;
  const task = searchParams.get('task') || 'Analyze this request';
  
  // Try to connect to backend first
  const useBackend = process.env.USE_BACKEND_AGENTS === 'true';
  
  if (useBackend) {
    try {
      const backendUrl = `${BACKEND_URL}/api/v1/stream/mission/${missionId}?task=${encodeURIComponent(task)}`;
      const response = await fetch(backendUrl, {
        headers: { 'Accept': 'text/event-stream' },
      });
      
      if (response.ok && response.body) {
        // Proxy the backend SSE stream
        return new Response(response.body, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
          },
        });
      }
    } catch (error) {
      console.log('Backend not available, using simulation mode');
    }
  }
  
  // Fallback to frontend simulation

  // Create a readable stream for SSE
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      // Helper to send SSE events
      const sendEvent = (type: string, data: any) => {
        const event = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
        controller.enqueue(encoder.encode(event));
      };

      try {
        // Send initial connection event
        sendEvent('connected', { missionId, timestamp: Date.now() });

        // Simulate agent workflow
        // In production, this would listen to Redis pub/sub or WebSocket from backend
        
        // Phase 1: Orchestrator starts
        sendEvent('agent_status', {
          agentId: 'flagpilot',
          status: 'thinking',
          action: 'Analyzing your request...',
        });
        
        await delay(1000);
        
        sendEvent('agent_thinking', {
          agentId: 'flagpilot',
          thought: 'Determining which agents to involve...',
        });
        
        await delay(1500);

        // Phase 2: Workflow update - show DAG
        sendEvent('workflow_update', {
          nodes: [
            { id: 'flagpilot', type: 'agent', position: { x: 250, y: 50 }, data: { agentId: 'flagpilot', status: 'working' } },
            { id: 'legal-eagle', type: 'agent', position: { x: 100, y: 200 }, data: { agentId: 'legal-eagle', status: 'waiting' } },
            { id: 'iris', type: 'agent', position: { x: 400, y: 200 }, data: { agentId: 'iris', status: 'waiting' } },
          ],
          edges: [
            { id: 'e1', source: 'flagpilot', target: 'legal-eagle', animated: true },
            { id: 'e2', source: 'flagpilot', target: 'iris', animated: true },
          ],
        });

        sendEvent('agent_status', {
          agentId: 'flagpilot',
          status: 'done',
          action: 'Task delegated',
        });

        await delay(500);

        // Phase 3: Parallel agent execution
        sendEvent('agent_status', {
          agentId: 'legal-eagle',
          status: 'working',
          action: 'Analyzing contract clauses...',
        });

        sendEvent('agent_status', {
          agentId: 'iris',
          status: 'working',
          action: 'Researching client background...',
        });

        await delay(2000);

        // Send partial results
        sendEvent('message', {
          agentId: 'legal-eagle',
          content: '**🔍 Initial Scan Complete**\n\nI\'ve identified 3 clauses that require attention...',
        });

        await delay(1000);

        sendEvent('agent_status', {
          agentId: 'legal-eagle',
          status: 'done',
        });

        sendEvent('agent_status', {
          agentId: 'iris',
          status: 'done',
        });

        await delay(500);

        // Phase 4: Generate UI component
        sendEvent('ui_component', {
          componentName: 'RiskAssessmentCard',
          props: {
            contractName: 'Sample_Contract.pdf',
            riskScore: 72,
            risks: [
              {
                id: 'risk-1',
                clause: 'Indemnification',
                severity: 'high',
                description: 'Broad indemnification clause exposes you to significant liability.',
                suggestion: 'Negotiate to limit indemnification to direct damages only.',
              },
              {
                id: 'risk-2',
                clause: 'Payment Terms',
                severity: 'medium',
                description: 'Net-60 payment terms are unfavorable.',
                suggestion: 'Request Net-30 or milestone-based payments.',
              },
            ],
          },
        });

        await delay(1000);

        // Final message
        sendEvent('message', {
          agentId: 'flagpilot',
          content: '## ✅ Analysis Complete\n\nI\'ve coordinated Legal Eagle and Iris to analyze your request. Here\'s what we found:\n\n- **2 contract risks** identified\n- **Client research** completed\n\nReview the Risk Assessment card above for detailed recommendations.',
        });

        // Mission complete
        sendEvent('mission_complete', { missionId });

      } catch (error) {
        sendEvent('error', { message: 'Stream error occurred' });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}

// Helper function
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
