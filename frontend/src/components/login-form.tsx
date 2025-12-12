"use client";

import { useState } from "react";
import { cn } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { SignInSocialButton } from "~/components/sign-in-social-button";
import { Link } from "@tanstack/react-router";
import { Shield, Github, Sparkles, ArrowRight, CheckCircle2 } from "lucide-react";

interface LoginFormProps extends React.ComponentProps<"div"> {
  redirectUrl?: string;
}

const benefits = [
  "AI-powered scam detection",
  "Smart contract analysis",
  "Client verification tools",
  "24/7 protection",
];

export function LoginForm({
  className,
  redirectUrl = "/dashboard",
  ...props
}: LoginFormProps) {
  const [hoveredProvider, setHoveredProvider] = useState<string | null>(null);

  return (
    <div className={cn("flex flex-col gap-8", className)} {...props}>
      <Card className="backdrop-blur-2xl bg-card/70 border-white/10 shadow-2xl rounded-3xl overflow-hidden">
        <CardHeader className="text-center pb-2 pt-8">
          {/* Animated Logo */}
          <div className="flex justify-center mb-4">
            <div className="relative group">
              <div className="absolute -inset-2 bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity duration-500" />
              <div className="relative h-16 w-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Shield className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          <CardTitle className="text-3xl font-bold tracking-tight">
            Welcome to FlagPilot
          </CardTitle>
          <CardDescription className="text-base mt-2">
            Your AI-powered freelance protection starts here
          </CardDescription>
        </CardHeader>

        <CardContent className="px-8 pb-8">
          {/* Benefits List */}
          <div className="mb-6 p-4 rounded-2xl bg-violet-500/5 border border-violet-500/10">
            <div className="grid grid-cols-2 gap-2">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-violet-500 flex-shrink-0" />
                  <span className="text-muted-foreground">{benefit}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-4">
            {/* GitHub Button */}
            <div
              onMouseEnter={() => setHoveredProvider("github")}
              onMouseLeave={() => setHoveredProvider(null)}
              className="relative group"
            >
              <div className={cn(
                "absolute -inset-0.5 bg-gradient-to-r from-gray-800 to-gray-600 rounded-xl blur-sm opacity-0 transition-opacity duration-300",
                hoveredProvider === "github" && "opacity-50"
              )} />
              <SignInSocialButton
                provider="github"
                callbackURL={redirectUrl}
                className={cn(
                  "relative w-full h-14 text-base rounded-xl transition-all duration-300",
                  "hover:scale-[1.02] active:scale-[0.98]"
                )}
                icon={
                  <Github className="h-5 w-5" />
                }
              />
            </div>

            {/* Google Button */}
            <div
              onMouseEnter={() => setHoveredProvider("google")}
              onMouseLeave={() => setHoveredProvider(null)}
              className="relative group"
            >
              <div className={cn(
                "absolute -inset-0.5 bg-gradient-to-r from-red-500 to-yellow-500 rounded-xl blur-sm opacity-0 transition-opacity duration-300",
                hoveredProvider === "google" && "opacity-50"
              )} />
              <SignInSocialButton
                provider="google"
                callbackURL={redirectUrl}
                className={cn(
                  "relative w-full h-14 text-base rounded-xl transition-all duration-300",
                  "hover:scale-[1.02] active:scale-[0.98]"
                )}
                icon={
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="h-5 w-5">
                    <path
                      d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
                      fill="currentColor"
                    />
                  </svg>
                }
              />
            </div>

            {/* Divider */}
            <div className="relative my-2">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-3 text-muted-foreground">
                  Secure & encrypted
                </span>
              </div>
            </div>

            {/* Terms */}
            <p className="text-center text-xs text-muted-foreground leading-relaxed">
              By continuing, you agree to our{" "}
              <a href="#" className="underline underline-offset-4 hover:text-violet-500 transition-colors">
                Terms of Service
              </a>{" "}
              and{" "}
              <a href="#" className="underline underline-offset-4 hover:text-violet-500 transition-colors">
                Privacy Policy
              </a>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Back to Home */}
      <div className="text-center">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group"
        >
          <ArrowRight className="h-4 w-4 rotate-180 group-hover:-translate-x-1 transition-transform" />
          Back to home
        </Link>
      </div>

      {/* Floating particles effect */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <Sparkles className="absolute top-10 right-10 h-4 w-4 text-violet-500/30 animate-pulse" />
        <Sparkles className="absolute bottom-20 left-10 h-3 w-3 text-purple-500/30 animate-pulse delay-300" />
        <Sparkles className="absolute top-1/3 left-5 h-2 w-2 text-violet-500/20 animate-pulse delay-500" />
      </div>
    </div>
  );
}
