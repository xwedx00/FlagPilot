# FlagPilot Frontend

**MGX.dev-Inspired Multi-Agent UI with War Room Interface**

Next.js 16 frontend for the FlagPilot freelancer protection platform. Features real-time agent workflow visualization, streaming chat, and Personal Data Moat management.

## ✨ Core Features

### 🎯 War Room Interface
- **Resizable Panels** - Chat + Visualizer/Artifacts/Data Moat
- **React Flow DAG** - Real-time workflow visualization with custom AgentNode
- **Live Console** - Streaming agent logs with color-coded output
- **Generative UI** - Dynamic RiskAssessmentCard, ClientDossierCard components

### 🔐 Authentication & Billing
- **Better Auth** - Session management with PostgreSQL
- **Polar.sh Credits** - Pay-per-agent-use billing
- **Credit Balance UI** - Real-time credit display and top-up

### 🛡️ Personal Data Moat
- **File Uploader** - Drag & drop with MinIO presigned URLs
- **File Browser** - Tree view with RAG embedding status
- **GDPR Compliance** - Data export and right to erasure page

### 🤖 AI Chat Integration
- **Vercel AI SDK** - Streaming chat with tool support
- **OpenRouter** - Claude/GPT model switching
- **Zustand Store** - Mission state management with stream event processing

### 🎨 MGX.dev Design System
- **Dark Industrial Theme** - Zinc 950 bg, emerald accents
- **Monospace Typography** - Geist Mono for terminal feel
- **Console-First UI** - Agent logs, code blocks, status badges

## 🚀 Tech Stack

- **Framework**: Next.js 15.3.1 with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v4 + shadcn/ui
- **Database**: Neon PostgreSQL + Drizzle ORM
- **Authentication**: Better Auth v1.2.8
- **Payments**: Polar.sh
- **AI**: OpenAI SDK
- **Storage**: Cloudflare R2
- **Analytics**: PostHog
- **Deployment**: Vercel (recommended)

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx                 # Landing/Login page
│   ├── mission/page.tsx         # War Room interface
│   ├── compliance/page.tsx      # GDPR compliance page
│   └── api/
│       ├── auth/[...all]/       # Better Auth endpoints
│       ├── chat/route.ts        # AI chat streaming
│       ├── mission/             # Mission SSE endpoints
│       └── files/               # File upload proxy
├── components/
│   ├── mission/                 # War Room components
│   │   ├── war-room.tsx         # Main container with panels
│   │   ├── visualizer.tsx       # React Flow DAG
│   │   ├── agent-node.tsx       # Custom node component
│   │   ├── live-console.tsx     # Agent log stream
│   │   └── index.ts
│   ├── billing/                 # Credit system UI
│   │   ├── credit-balance.tsx   # Balance display
│   │   ├── pricing-cards.tsx    # Subscription tiers
│   │   └── usage-history.tsx    # Transaction log
│   ├── moat/                    # Data Moat UI
│   │   ├── file-uploader.tsx    # Dropzone upload
│   │   └── file-tree.tsx        # File browser
│   ├── generative-ui/           # Agent output cards
│   │   ├── risk-assessment-card.tsx
│   │   ├── client-dossier-card.tsx
│   │   ├── contract-redline.tsx
│   │   └── negotiation-script.tsx
│   └── ui/                      # shadcn/ui components
├── stores/
│   └── mission-store.ts         # Zustand state management
├── lib/
│   ├── auth.ts                  # Better Auth config
│   ├── auth-client.ts           # Client-side auth
│   └── utils.ts                 # Utilities
└── db/
    ├── schema.ts                # Drizzle schema
    └── drizzle.ts               # Database connection
```

## 🛠️ Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL database (Neon recommended)
- Cloudflare R2 bucket for file storage
- Polar.sh account for subscriptions
- OpenAI API key for AI features
- Google OAuth credentials (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd next-starter-2.0
```

2. **Install dependencies**
```bash
pnpm install
```

3. **Environment Setup**
Create a `.env.local` file with:
```env
# Database
DATABASE_URL="your-neon-database-url"

# Authentication
BETTER_AUTH_SECRET="your-secret-key"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Polar.sh
POLAR_ACCESS_TOKEN="your-polar-access-token"
POLAR_WEBHOOK_SECRET="your-webhook-secret"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"

# Cloudflare R2 Storage
CLOUDFLARE_ACCOUNT_ID="your-cloudflare-account-id"
R2_UPLOAD_IMAGE_ACCESS_KEY_ID="your-r2-access-key-id"
R2_UPLOAD_IMAGE_SECRET_ACCESS_KEY="your-r2-secret-access-key"
R2_UPLOAD_IMAGE_BUCKET_NAME="your-r2-bucket-name"

# Polar.sh Pricing Tiers
NEXT_PUBLIC_STARTER_TIER="your-starter-product-id"
NEXT_PUBLIC_STARTER_SLUG="your-starter-slug"
```

4. **Database Setup**
```bash
# Generate and run migrations
npx drizzle-kit generate
npx drizzle-kit push
```

5. **Cloudflare R2 Setup**
- Create a Cloudflare account and set up R2 storage
- Create a bucket for file uploads
- Generate API tokens with R2 permissions
- Configure CORS settings for your domain

6. **Polar.sh Setup**
- Create products for your pricing tiers
- Set up webhook endpoints for subscription events
- Configure your pricing structure

7. **Start Development Server**
```bash
pnpm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your application.

## 🎯 Key Features Explained

### Subscription Management
- Automatic subscription status checking
- Payment gating for premium features
- Integration with Polar.sh customer portal
- Webhook handling for real-time updates

### AI Chat Integration
- Built-in chatbot with OpenAI
- Markdown rendering for rich responses
- Conversation history and context

### File Upload System
- **Cloudflare R2 integration** with S3-compatible API
- **Drag & drop interface** with visual feedback
- **File validation** - Type checking and size limits
- **Progress tracking** - Real-time upload progress
- **Image gallery** - View uploaded files with metadata
- **Copy URLs** - Easy sharing and integration

### Analytics & Tracking
- PostHog event tracking
- User behavior monitoring
- Custom analytics dashboard

## 🔧 Customization

### Adding New Features
1. Create components in `components/`
2. Add API routes in `app/api/`
3. Update database schema in `db/schema.ts`
4. Run `npx drizzle-kit generate` and `npx drizzle-kit push`

### Styling
- Modify `app/globals.css` for global styles
- Use Tailwind classes for component styling
- Customize theme in `tailwind.config.ts`

### Authentication
- Configure providers in `lib/auth/auth.ts`
- Add new OAuth providers as needed
- Customize user profile fields in database schema

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://better-auth.com)
- [Polar.sh Documentation](https://docs.polar.sh)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Add environment variables in Vercel dashboard
3. Deploy automatically on every push

### Manual Deployment
```bash
pnpm run build
pnpm start
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using Next.js and modern web technologies.
