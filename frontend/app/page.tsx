"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { LoginScreen } from "@/components/login-screen";
import { OnboardingModal } from "@/components/onboarding-modal";
import { Loader } from "@/components/ui/loader";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { AppLayout } from "@/components/flagpilot";
import { useCredits } from "@/hooks/use-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  FileText, 
  Search, 
  DollarSign, 
  Shield, 
  Plus, 
  ArrowRight,
  Zap,
  Bot,
} from "lucide-react";

// Quick action cards for dashboard
function QuickActionCard({ 
  icon: Icon, 
  title, 
  description, 
  onClick 
}: { 
  icon: React.ElementType; 
  title: string; 
  description: string;
  onClick: () => void;
}) {
  return (
    <Card 
      className="cursor-pointer transition-all hover:border-primary/50 hover:bg-card/80 active:scale-[0.98] group"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Icon className="size-5 text-primary" />
          </div>
          <ArrowRight className="size-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </CardHeader>
      <CardContent>
        <CardTitle className="text-base mb-1">{title}</CardTitle>
        <CardDescription className="text-sm">{description}</CardDescription>
      </CardContent>
    </Card>
  );
}

// Dashboard content
function DashboardContent({ 
  onStartMission 
}: { 
  onStartMission: (type: string) => void;
}) {
  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Welcome Section */}
        <div className="text-center space-y-4 py-8">
          <div className="flex justify-center">
            <div className="size-16 rounded-2xl bg-primary/20 flex items-center justify-center">
              <Zap className="size-8 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome to FlagPilot
          </h1>
          <p className="text-muted-foreground max-w-lg mx-auto">
            13 specialized AI agents working together to protect your freelance career. 
            Start a mission to analyze contracts, verify jobs, or collect payments.
          </p>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Bot className="size-5" />
            Quick Actions
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <QuickActionCard
              icon={FileText}
              title="Contract Review"
              description="AI-powered contract analysis"
              onClick={() => onStartMission("contract")}
            />
            <QuickActionCard
              icon={Search}
              title="Job Verification"
              description="Verify client legitimacy"
              onClick={() => onStartMission("verification")}
            />
            <QuickActionCard
              icon={DollarSign}
              title="Payment Collection"
              description="Chase overdue invoices"
              onClick={() => onStartMission("payment")}
            />
            <QuickActionCard
              icon={Shield}
              title="Dispute Resolution"
              description="Resolve client conflicts"
              onClick={() => onStartMission("dispute")}
            />
          </div>
        </div>

        {/* Start Mission CTA */}
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardContent className="flex flex-col md:flex-row items-center justify-between gap-4 p-6">
            <div>
              <h3 className="text-lg font-semibold mb-1">Ready to start?</h3>
              <p className="text-muted-foreground text-sm">
                Describe your task and let the AI agents handle the rest.
              </p>
            </div>
            <Button 
              size="lg" 
              className="gap-2"
              onClick={() => onStartMission("general")}
            >
              <Plus className="size-4" />
              New Mission
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [session, setSession] = useState<any>(null);
  const [onboardingRequired, setOnboardingRequired] = useState(false);
  
  // Fetch real credits from backend API
  const { balance, isLoading: creditsLoading } = useCredits();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data } = await authClient.getSession();
        setSession(data);
        
        if (data?.user) {
          try {
            const profileRes = await fetch(`/api/user/profile?userId=${data.user.id}`);
            const profile = await profileRes.json();
            
            if (!profile || !profile.onboardingCompleted) {
              const localComplete = localStorage.getItem(`onboarding_completed_${data.user.id}`);
              if (!localComplete) {
                setOnboardingRequired(true);
              }
            }
          } catch {
            if (!localStorage.getItem(`onboarding_completed_${data.user.id}`)) {
              setOnboardingRequired(true);
            }
          }
        }
      } catch (error) {
        console.log("Auth check:", error instanceof Error ? error.message : "Not authenticated");
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleOnboardingComplete = () => {
    if (session?.user?.id) {
      localStorage.setItem(`onboarding_completed_${session.user.id}`, "true");
    }
    setOnboardingRequired(false);
    toast.success("Welcome to FlagPilot!", {
      description: "Your profile has been set up. Our AI agents are ready to protect your freelance career.",
    });
  };

  const handleOnboardingOpenChange = (open: boolean) => {
    if (!open && onboardingRequired) {
      toast.info("Please complete onboarding first", {
        description: "You need to complete the setup to use FlagPilot.",
      });
      return;
    }
    setOnboardingRequired(open);
  };

  const handleStartMission = useCallback((type: string) => {
    router.push(`/mission?type=${type}`);
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader variant="circular" size="lg" />
          <p className="text-muted-foreground text-sm">Loading FlagPilot...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return <LoginScreen />;
  }

  return (
    <>
      <Toaster position="top-right" richColors closeButton />
      <AppLayout
        breadcrumbs={[{ label: "Home" }]}
        user={{
          name: session.user?.name || "User",
          email: session.user?.email || "",
          avatarUrl: session.user?.image || undefined,
        }}
        credits={balance ? { current: balance.current, total: balance.total } : { current: 0, total: 0 }}
      >
        <DashboardContent onStartMission={handleStartMission} />
      </AppLayout>
      <OnboardingModal
        open={onboardingRequired}
        onOpenChange={handleOnboardingOpenChange}
        user={session.user}
        onComplete={handleOnboardingComplete}
      />
    </>
  );
}
