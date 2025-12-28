# FlagPilot Frontend (v7.0) - Developer Guide
> **The Real Implementation Reference**

## ⚡ Tech Stack (Verified)
*   **Framework**: Next.js 16.1.1 (App Router)
*   **Core Logic**: React 19.2.3 (Server Components)
*   **Styling**: TailwindCSS v4 (PostCSS)
*   **Animations**: GSAP 3.14.2
*   **Auth**: Better-Auth v1.4.9
*   **AI Integration**: CopilotKit v1.50.1 (AG-UI Protocol)

## 📂 Project Structure (Annotated)

```text
frontend/
├── app/
│   ├── api/
│   │   ├── copilotkit/     # Route Handler for AG-UI Protocol (connects to Backend)
│   │   └── auth/           # Better-Auth API routes (api/auth/[...all])
│   ├── chat/               # Main Chat Interface (/chat)
│   ├── layout.tsx          # Root Layout. Defines <CopilotKit> provider.
│   └── globals.css         # Tailwind v4 directives.
├── components/
│   ├── chat/
│   │   ├── chat-interface.tsx  # CORE State Manager. Uses useFlagPilotActions.
│   │   ├── copilot-command.tsx # CMDK Palette with GSAP animations.
│   │   └── memory-panel.tsx    # Collapsible memory view.
│   └── ui/                     # Shadcn UI (Radix Primitives).
├── lib/
│   ├── auth.ts                 # Better-Auth Config (Postgres Adapter).
│   ├── hooks/
│   │   ├── use-flagpilot-actions.ts # DEFINES CopilotActions (Tools).
│   │   └── use-flagpilot-state.ts   # Handles AG-UI State streaming.
│   └── schema.ts               # Drizzle ORM Schema (User, Session, Account).
└── middlewares.ts              # (If applicable - check implementation)
```

## 🚀 Setup & Run
**Uses Bun as Package Manager**.

1.  **Install Dependencies**:
    ```bash
    bun install
    ```
2.  **Dev Server**:
    ```bash
    bun dev
    # Runs on http://localhost:3000
    ```

## 🔐 Environment Variables
Required in `.env`:
*   `BETTER_AUTH_URL`: e.g., `http://localhost:3000`
*   `BACKEND_COPILOT_URL`: e.g., `http://127.0.0.1:8000/copilotkit` (Agent Endpoint)
*   `DATABASE_URL`: Postgres Connection String (for Auth)
*   `BETTER_AUTH_SECRET`: Random Secret
