# FlagPilot Frontend

Modern AI-powered freelancer protection platform built with Next.js 15, Shadcn UI, and CopilotKit.

## Tech Stack

- **Framework**: [Next.js 15 (App Router)](https://nextjs.org)
- **Language**: TypeScript
- **UI Library**: [Shadcn UI](https://ui.shadcn.com) + Tailwind CSS 4
- **Authentication**: [Better Auth](https://better-auth.com) (GitHub & Google)
- **AI Integration**: [CopilotKit](https://docs.copilotkit.ai) (CoAgents)
- **Database ORM**: [Drizzle ORM](https://orm.drizzle.team) (PostgreSQL)
- **Package Manager**: [Bun](https://bun.sh)

## Features

- **AI Chat Interface**: Real-time interaction with FlagPilot agents via CopilotKit.
- **Secure Authentication**: Passwordless login via GitHub and Google.
- **Responsive Design**: Premium dark-mode UI with smooth animations.
- **Agent Discovery**: Auto-syncs with backend agents (`flagpilot_orchestrator`).

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

- `/app`: Next.js App Router pages and API routes.
- `/components`: Reusable UI components (Shadcn).
- `/lib`: Utilities, database connection, and auth configuration.
- `/public`: Static assets.

## Integration with Backend (AG-UI)
The frontend communicates with the FastAPI backend via the **AG-UI Protocol**:

1.  **Proxy Configuration**:
    - `next.config.ts` proxies `/api/agui/*` -> `http://127.0.0.1:8000/api/agui/*`.
    
2.  **CopilotKit Runtime**:
    - Root Layout (`app/layout.tsx`) configures `<CopilotKit runtimeUrl="/api/agui" />`.
    - This enables auto-discovery of agents like `flagpilot_orchestrator`.

3.  **Authentication**:
    - Better Auth sessions are managed via `lib/auth.ts`.
    - Future: Session tokens will be passed to `/api/agui` headers for backend context.

