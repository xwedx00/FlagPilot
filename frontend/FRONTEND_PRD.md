# FlagPilot Frontend PRD (Technical Spec)
**Status**: Verified Implementation (Next.js 16 + CopilotKit 1.50)

## 1. User Flows

### 1.1 Authentication Journey
*   **Entry**: Users land on `/login`.
*   **Mechanism**: Better-Auth handles identity via `api/auth/[...all]`.
*   **Session**: Persisted in PostgreSQL (`user`, `session` tables via Drizzle).
*   **Redirect**: Upon success, middleware redirects to `/chat`.

### 1.2 The Chat Experience
*   **Route**: `/chat` is the primary authenticated view.
*   **Layout**:
    *   **Header**: Shows "FlagPilot Orchestrator" status (`Processing...` vs `17 Agents Ready`).
    *   **Main Area**: `<CopilotChat>` component handles message history and scrolling.
    *   **Panels**:
        *   **Memory Panel**: Collapsible side view (toggled by state).
        *   **Command Palette**: Triggered by `⌘K`.

## 2. CopilotKit Architecture (AG-UI Protocol)

### 2.1 Backend Connection
The frontend acts as a "Headless Host" for the backend LangGraph agent.
*   **Provider**: `<CopilotKit runtimeUrl="/api/copilotkit" agent="flagpilot_orchestrator">` in `layout.tsx`.
*   **Route Handler**: `app/api/copilotkit/route.ts` uses `LangGraphHttpAgent` to tunnel requests to the FastAPI backend.
*   **Protocol**: Requests are proxied; the backend executes the graph and streams state updates (JSON patches) back to the UI.

### 2.2 Frontend "Tools" (Actions)
Defined in `lib/hooks/use-flagpilot-actions.ts`. These allow the *Backend Agents* to control the *Frontend UI*.

| Action Name | Logic | Triggered By |
| :--- | :--- | :--- |
| `toggleMemoryPanel` | Toggles React state `showMemory`. | User (⌘K) or Agent ("I'll open your memory panel...") |
| `showRiskAlert` | Sets `riskAlert` state to display a warning modal. | RiskAdvisor Agent (High Risk detected) |
| `exportChat` | Console log stub (TODO). | User (Command Palette) |

### 2.3 State Management
*   **`useFlagPilotState` Hook**:
    *   Subscribes to the AG-UI stream.
    *   Parses `agentState` (current node, status) to update the UI "Processing" indicator.
    *   Renders specific UI components (like Status Badges) based on the active backend agent (e.g., "ContractGuardian is analyzing...").

## 3. UI/UX Internals

### 3.1 Command Palette (`copilot-command.tsx`)
*   **Tech**: `cmdk` primitive + GSAP animations.
*   **Logic**:
    *   Listens for `⌘K` global keydown.
    *   GSAP `stagger` effect runs on open (`listRef.current`).
    *   **Actions**: Clicking an item (e.g., "Analyze Contract") sends a preset prompt to the Copilot via `appendMessage` (handled in parent).

### 3.2 Threading & Persistence
*   **Sessions**: Uses CopilotKit's built-in session management.
*   **Thread ID**: Stored in URL query param or local storage (implementation detail) to resume backend threads.

## 4. Confirmed Constraints & Versions
*   **Next.js 16**: Uses React 19 features. `force-dynamic` is used on `/chat` to preventing caching issues with auth.
*   **Tailwind v4**: New configuration strategy (CSS-based config in `globals.css`).
*   **Hydration**: `suppressHydrationWarning` is applied to `<body>` to handle theme providers and CopilotKit injection.
