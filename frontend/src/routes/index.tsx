import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Suspense } from "react";
import { Shield, Sparkles, Users, FileSearch, MessageSquare, Zap } from "lucide-react";
import { Banner } from "~/components/billingsdk/banner";
import { FlagPilotHeader } from "~/components/flagpilot-header";
import { PricingTableSix } from "~/components/billingsdk/pricing-table-six";
import { ShaderVoid } from "~/components/shader-void";
import { Button } from "~/components/ui/button";
import { authQueryOptions } from "~/lib/auth/queries";

export const Route = createFileRoute("/")({
  component: HomePage,
});

const gradientColors = [
  "rgba(139,92,246,0.6)",
  "rgba(168,85,247,0.7)",
  "rgba(192,132,252,0.5)",
  "rgba(139,92,246,0.6)",
];

const pricingPlans = [
  {
    id: "free",
    title: "Free",
    description: "Perfect for getting started with freelance protection",
    monthlyPrice: 0,
    yearlyPrice: 0,
    features: [
      "5 client scans per month",
      "Basic red flag detection",
      "Contract keyword alerts",
      "Email support",
      "Community access",
    ],
  },
  {
    id: "pro",
    title: "Pro",
    description: "For serious freelancers who need full protection",
    monthlyPrice: 19,
    yearlyPrice: 190,
    isFeatured: true,
    features: [
      "Unlimited client scans",
      "Advanced AI risk analysis",
      "Contract review & suggestions",
      "Payment timeline tracking",
      "Negotiation coaching",
      "Priority support",
    ],
  },
  {
    id: "enterprise",
    title: "Enterprise",
    description: "Custom solutions for agencies and teams",
    monthlyPrice: 99,
    yearlyPrice: 990,
    isCustom: true,
    features: [
      "Everything in Pro",
      "Multi-user team access",
      "Custom API integrations",
      "Dedicated account manager",
      "SLA guarantee",
      "Custom training",
    ],
  },
];

const features = [
  {
    icon: Shield,
    title: "Scam Detection",
    description: "AI-powered analysis to identify red flags in client communications and contracts",
  },
  {
    icon: FileSearch,
    title: "Contract Review",
    description: "Smart contract analysis with suggestions to protect your interests",
  },
  {
    icon: Users,
    title: "Client Verification",
    description: "Verify client legitimacy before committing to projects",
  },
  {
    icon: MessageSquare,
    title: "Negotiation Coach",
    description: "AI-assisted guidance for difficult client conversations",
  },
  {
    icon: Zap,
    title: "Fast Workflows",
    description: "Automated agents handle repetitive tasks so you focus on work",
  },
  {
    icon: Sparkles,
    title: "Smart Insights",
    description: "Learn from patterns to improve your freelance business",
  },
];

function HomePage() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background">
      {/* Animated Background */}
      <ShaderVoid
        voidBallsAmount={3}
        width={1300}
        height={1100}
        voidBallsColor="#8b5cf6"
        plasmaBallsColor="#a855f7"
        plasmaBallsStroke="#c084fc"
        gooeyCircleSize={30}
        blendMode="overlay"
        className="fixed inset-0 h-full w-full"
      />

      {/* Gradient Banner at Top */}
      <Banner
        title="🚀 FlagPilot Beta is Live!"
        description="Join thousands of freelancers protecting their careers with AI"
        buttonText="Get Started Free"
        buttonLink="/login"
        variant="default"
        gradientColors={gradientColors}
        dismissable={true}
      />

      {/* Main Container - Glassmorphism Box */}
      <div className="relative z-10 mx-auto max-w-7xl p-4 md:p-8">
        <div className="min-h-screen rounded-3xl border border-white/10 bg-background/30 backdrop-blur-2xl shadow-2xl overflow-hidden">

          {/* Header */}
          <FlagPilotHeader />

          {/* Hero Section */}
          <section id="hero" className="relative px-6 py-16 md:px-12 md:py-24">
            <div className="max-w-4xl">
              <div className="mb-6 inline-flex items-center rounded-full bg-violet-500/10 border border-violet-500/20 px-4 py-2">
                <Sparkles className="h-4 w-4 mr-2 text-violet-500" />
                <span className="text-sm font-medium text-violet-600 dark:text-violet-400">
                  AI-Powered Freelance Protection
                </span>
              </div>

              <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6 leading-tight">
                <span className="italic font-light">Protect</span> Your
                <br />
                <span className="bg-gradient-to-r from-violet-500 to-purple-600 bg-clip-text text-transparent">
                  Freelance Career
                </span>
              </h1>

              <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl leading-relaxed">
                FlagPilot uses AI agents to shield freelancers from scams,
                review contracts, verify clients, and coach you through tough negotiations.
                <span className="font-semibold text-foreground"> Your AI guard dog for the gig economy.</span>
              </p>

              <div className="flex flex-wrap gap-4">
                <Button
                  size="lg"
                  asChild
                  className="h-14 px-8 text-lg rounded-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-violet-500/30 transition-all"
                >
                  <Link to="/login">
                    <Shield className="h-5 w-5 mr-2" />
                    Get Protected Free
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  asChild
                  className="h-14 px-8 text-lg rounded-full border-2 hover:bg-accent"
                >
                  <a href="#pricing">See Pricing</a>
                </Button>
              </div>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="px-6 py-16 md:px-12 border-t border-white/10">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-5xl font-bold mb-4">
                Everything you need to{" "}
                <span className="italic font-light">stay safe</span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Comprehensive protection powered by advanced AI agents working 24/7
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="group rounded-2xl border border-white/10 bg-white/5 p-6 transition-all duration-300 hover:bg-white/10 hover:border-violet-500/30 hover:-translate-y-1"
                >
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-600/20 group-hover:from-violet-500/30 group-hover:to-purple-600/30 transition-colors">
                    <feature.icon className="h-6 w-6 text-violet-500" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Pricing Section */}
          <section id="pricing" className="border-t border-white/10">
            <PricingTableSix
              plans={pricingPlans}
              onPlanSelect={(planId) => {
                console.log("Selected plan:", planId);
                window.location.href = "/login";
              }}
            />
          </section>

          {/* CTA Section */}
          <section className="px-6 py-16 md:px-12 border-t border-white/10 text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Ready to protect your freelance career?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of freelancers who trust FlagPilot to keep them safe
            </p>
            <Button
              size="lg"
              asChild
              className="h-14 px-10 text-lg rounded-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-violet-500/30 transition-all"
            >
              <Link to="/login">
                <Shield className="h-5 w-5 mr-2" />
                Start Free Today
              </Link>
            </Button>
          </section>

          {/* Footer */}
          <footer className="px-6 py-8 md:px-12 border-t border-white/10">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-violet-500" />
                <span className="font-semibold text-foreground">FlagPilot</span>
                <span>© 2024 All rights reserved.</span>
              </div>
              <div className="flex gap-6">
                <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
                <a href="#" className="hover:text-foreground transition-colors">Terms</a>
                <a href="#" className="hover:text-foreground transition-colors">Contact</a>
              </div>
            </div>
          </footer>
        </div>
      </div>

      {/* User Status Banner */}
      <Suspense fallback={null}>
        <UserStatusBanner />
      </Suspense>
    </div>
  );
}

function UserStatusBanner() {
  const { data: user } = useSuspenseQuery(authQueryOptions());

  if (!user) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="bg-card/90 backdrop-blur-xl border rounded-2xl p-4 shadow-2xl">
        <p className="text-sm mb-2">Welcome back, <span className="font-semibold">{user.name}</span>!</p>
        <Button asChild size="sm" className="w-full rounded-full bg-gradient-to-r from-violet-500 to-purple-600">
          <Link to="/dashboard">Go to Dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
