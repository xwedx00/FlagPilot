import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Suspense } from "react";
import { HeroSection } from "~/components/hero-section";
import { ShaderVoid } from "~/components/shader-void";
import { Button } from "~/components/ui/button";
import { authQueryOptions } from "~/lib/auth/queries";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="relative flex min-h-svh w-full flex-col items-center justify-center overflow-hidden">
      <ShaderVoid
        voidBallsAmount={3}
        width={1300}
        height={1100}
        voidBallsColor="#8b5cf6"
        plasmaBallsColor="#a855f7"
        plasmaBallsStroke="#c084fc"
        gooeyCircleSize={30}
        blendMode="overlay"
        className="absolute inset-0 mx-auto h-full w-full"
      />
      <HeroSection />

      {/* Quick User Status */}
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
      <div className="bg-card/90 backdrop-blur-md border rounded-lg p-4 shadow-lg">
        <p className="text-sm mb-2">Welcome back, {user.name}!</p>
        <Button asChild size="sm">
          <Link to="/dashboard">Go to Dashboard</Link>
        </Button>
      </div>
    </div>
  );
}
