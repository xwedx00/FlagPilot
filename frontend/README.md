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

## Project Structure

- `/app`: Next.js App Router pages and API routes.
- `/components`: Reusable UI components (Shadcn).
- `/lib`: Utilities, database connection, and auth configuration.
- `/public`: Static assets.

## Integration with Backend

The frontend communicates with the FastAPI backend via:
- **Proxy**: `/api/agui/*` requests are proxied to `http://127.0.0.1:8000/api/agui/*`.
- **CopilotKit**: Connects to the runtime URL `/api/agui` to discover and interact with agents.
