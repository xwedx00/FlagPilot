
"use client";

import { authClient } from "@/lib/auth-client";
import { AnimatedButton } from "@/components/ui/animated-button";
import { AnimatedCard, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/animated-card";
import { Github, Loader2, AlertCircle, Shield } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function SignIn() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSignIn = async (provider: "github" | "google") => {
        setLoading(true);
        setError(null);
        await authClient.signIn.social({
            provider: provider,
            callbackURL: "/chat"
        }, {
            onRequest: () => {
                setLoading(true);
            },
            onSuccess: () => {
                router.push("/chat");
            },
            onError: (ctx) => {
                // BetterAuth returns 409 or specific messages for linking conflicts
                if (ctx.error.status === 409 ||
                    ctx.error.message?.toLowerCase().includes("linked") ||
                    ctx.error.message?.toLowerCase().includes("exists")) {
                    setError("Access Denied: An account with this email already exists using a different provider. Please sign in with the original provider.");
                } else {
                    setError(ctx.error.message || "An error occurred during sign in.");
                }
                setLoading(false);
            }
        });
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-950 to-indigo-950 p-4">
            <AnimatedCard className="w-full max-w-md bg-zinc-900/80 backdrop-blur-sm border-zinc-800">
                <CardHeader className="text-center">
                    <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                        <Shield className="w-8 h-8 text-white" />
                    </div>
                    <CardTitle className="text-2xl text-white">Welcome to FlagPilot</CardTitle>
                    <CardDescription className="text-zinc-400">Sign in to access your intelligent agent team</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {error && (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Sign In Failed</AlertTitle>
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    <AnimatedButton
                        onClick={() => handleSignIn("github")}
                        className="w-full flex items-center gap-2"
                        variant="outline"
                        disabled={loading}
                    >
                        {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Github className="w-4 h-4" />}
                        Continue with GitHub
                    </AnimatedButton>
                    <AnimatedButton
                        onClick={() => handleSignIn("google")}
                        className="w-full flex items-center gap-2"
                        variant="outline"
                        disabled={loading}
                    >
                        {loading ? <Loader2 className="animate-spin w-4 h-4" /> : (
                            <svg className="w-4 h-4" viewBox="0 0 24 24">
                                <path
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    fill="#4285F4"
                                />
                                <path
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                    fill="#34A853"
                                />
                                <path
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                    fill="#FBBC05"
                                />
                                <path
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    fill="#EA4335"
                                />
                            </svg>
                        )}
                        Continue with Google
                    </AnimatedButton>
                </CardContent>
            </AnimatedCard>
        </div>
    );
}
