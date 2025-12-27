# FlagPilot Frontend v6.1

Modern AI-powered freelancer protection platform built with Next.js 15, Shadcn UI, and CopilotKit.

## Tech Stack

- **Framework**: [Next.js 15 (App Router)](https://nextjs.org)
- **Language**: TypeScript
- **UI Library**: [Shadcn UI](https://ui.shadcn.com) + Tailwind CSS 4
- **Authentication**: [Better Auth](https://better-auth.com) (GitHub & Google)
- **AI Integration**: [CopilotKit](https://docs.copilotkit.ai) (AG-UI Protocol)
- **Database ORM**: [Drizzle ORM](https://orm.drizzle.team) (PostgreSQL)
- **Package Manager**: [Bun](https://bun.sh)
- **Animations**: [GSAP](https://greensock.com/gsap/)

## Features

### Core Features
- **AI Chat Interface**: Real-time interaction with 17 FlagPilot agents via CopilotKit.
- **Secure Authentication**: Passwordless login via GitHub and Google.
- **Responsive Design**: Premium dark-mode UI with smooth animations.
- **Agent Discovery**: Auto-syncs with backend agents (`flagpilot_orchestrator`).

### New in v6.1 (Smart-Stack)
- **Command Palette (⌘K)**: Quick access to agents and actions with GSAP animations.
- **AI-Controlled UI**: CopilotKit actions for `toggleMemoryPanel`, `showRiskAlert`, `exportChatHistory`.
- **Memory Panel**: View user profile, recent sessions, and global wisdom.
- **Risk Alerts**: Visual warnings for critical scam/fraud detection.

## Getting Started

### Prerequisites

- Node.js 18+ or Bun 1.0+
- PostgreSQL Database
- FlagPilot Backend running at `http://localhost:8000`

### Installation

1. Install dependencies:
   ```bash
   bun install
   ```

2. Configure Environment:
   Copy `.env.example` to `.env` (or create it) and add:
   ```env
   BETTER_AUTH_SECRET=your_generated_secret_here
   BETTER_AUTH_URL=http://localhost:3000
   GITHUB_CLIENT_ID=...
   GITHUB_CLIENT_SECRET=...
   DATABASE_URL=postgresql://user:pass@localhost:5432/flagpilot
   
   # Suppress Node deprecation warnings
   NODE_OPTIONS="--no-deprecation"
   ```

3. Run Database Migrations:
   ```bash
   bun run db:push
   ```

4. Start Development Server:
   ```bash
   bun dev
   ```

## Key Components

### Command Palette (`copilot-command.tsx`)
Press `⌘K` to open a command palette with:
- **6 Agent Shortcuts**: Contract, Scam, Payment, Rate, Message, Profile
- **4 Quick Actions**: Memory, Search, Export, Clear
- GSAP stagger animations on open

### Chat Interface (`chat-interface.tsx`)
Main chat UI with:
- CopilotKit integration
- Agent status display (17 Agents Ready)
- Memory panel toggle
- Risk alert display

### CopilotKit Actions (`use-flagpilot-actions.ts`)
Custom hooks for:
- `toggleMemoryPanel`: Open/close memory panel
- `showRiskAlert`: Display critical warnings
- `exportChatHistory`: Trigger chat export

## Authentication
This project uses **BetterAuth** with PostgreSQL (Drizzle ORM).
- **Providers**: GitHub, Google (Email/Password disabled).
- **Strict Isolation**: Account linking is DISABLED. Users cannot link multiple providers to the same email.
- **Middleware**: Routes are protected via `proxy.ts` (Next.js 16+ convention).
- **Database**:
  - Run `bun reset-db.js` to wipe and reset the schema.
  - Run `bun drizzle-kit push` to apply schema changes.

## Development
1. `bun install`
2. `bun dev` (Runs on localhost:3000)
3. `bun run build` (Production build)

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   ├── copilotkit/route.ts  # CopilotKit API route
│   │   └── auth/[...all]/route.ts
│   ├── chat/page.tsx            # Main chat page
│   ├── login/page.tsx
│   └── layout.tsx               # CopilotKit provider
├── components/
│   ├── chat/
│   │   ├── chat-interface.tsx   # Main chat UI
│   │   └── copilot-command.tsx  # Command palette (NEW)
│   └── ui/                      # Shadcn components
├── lib/
│   ├── hooks/
│   │   └── use-flagpilot-actions.ts  # CopilotKit actions (UPDATED)
│   ├── auth.ts
│   └── db/
└── public/
```

## Integration with Backend (CopilotKit/AG-UI)
The frontend communicates with the FastAPI backend via the **CopilotKit AG-UI Protocol**:

1.  **CopilotKit Route**:
    - `app/api/copilotkit/route.ts` uses `ExperimentalEmptyAdapter` since the backend handles all LLM calls.
    - Backend endpoint: `http://127.0.0.1:8000/copilotkit`
    
2.  **CopilotKit Runtime**:
    - Root Layout configures `<CopilotKit runtimeUrl="/api/copilotkit" />`.
    - This enables auto-discovery of agents like `flagpilot_orchestrator`.

3.  **UI Control Actions**:
    - Backend agents can trigger frontend actions via CopilotKit.
    - Example: `toggleMemoryPanel`, `showRiskAlert`

## Version History

- **v6.1.0** - Smart-Stack Edition
  - Command Palette with GSAP animations
  - AI-controlled UI actions
  - Memory panel improvements
  - Risk alert display

- **v6.0.0** - CopilotKit integration
  - AG-UI protocol streaming
  - Agent discovery
