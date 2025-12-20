# Phase 4: Frontend Chat Integration Plan

## Goal
Implement a premium, responsive Chat Interface in the frontend that connects to the FlagPilot backend via AG-UI/CopilotKit. This interface will allow users to interact with the Multi-Agent Team (Orchestrator).

## User Review Required
> [!IMPORTANT]
> This plan assumes the backend is running on `http://localhost:8000` and the Next.js proxy is correctly configured in `next.config.ts`.

## Proposed Changes

### Frontend Components

#### [NEW] [chat-interface.tsx](file:///c:/Users/Yalo/Desktop/Flag-Project/frontend/components/chat/chat-interface.tsx)
- Custom wrapper around CopilotKit's `useCopilotChat`.
- **Features**:
    - Real-time streaming message list.
    - Custom message bubbles (User vs System vs Agent).
    - "Activity Indicator" for showing which agent is currently working (using `ActivitySnapshot` events if supported, or standard loading states).
    - Input area with attachment support (future proofing).

#### [NEW] [page.tsx](file:///c:/Users/Yalo/Desktop/Flag-Project/frontend/app/chat/page.tsx)
- Main route for the chat functionality.
- Protected by authentication.
- Layout: Sidebar (History/Agents) + Main Chat Area.

#### [MODIFY] [layout.tsx](file:///c:/Users/Yalo/Desktop/Flag-Project/frontend/app/layout.tsx)
- Ensure `CopilotSidebar` is configured or removed if building a custom full-page chat (User requested "Chat" so a full page is better than a sidebar).
- Verify `runtimeUrl="/api/agui"`.

### Styling
- **Tailwind**: Use `zinc` or `slate` colors for a professional, premium look.
- **Animations**: `framer-motion` for message appearance and typing indicators.

## Verification Plan

### Automated
- Browser test: Navigate to `/chat`, type a message, verify response streams in.

### Manual
1.  Login via GitHub.
2.  Go to `/chat`.
3.  Type: "I recently received a job offer via Telegram."
4.  Verify:
    - Message appears immediately.
    - "Orchestrator" thinks.
    - "Risk Advisor" agent (if triggered) output appears.
    - Final synthesis is displayed.
