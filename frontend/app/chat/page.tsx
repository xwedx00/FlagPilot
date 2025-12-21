import { ChatInterface } from "@/components/chat/chat-interface";
import { Metadata } from "next";

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
    title: "Chat | FlagPilot",
    description: "AI-Powered Freelancer Protection",
};

export default function ChatPage() {
    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex flex-col items-center justify-center p-4 md:p-8">
            <div className="w-full max-w-5xl space-y-4">
                <div className="text-center space-y-2 mb-8">
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                        FlagPilot Intelligence
                    </h1>
                    <p className="text-zinc-500 dark:text-zinc-400">
                        Secure, multi-agent analysis for your contracts and client interactions.
                    </p>
                </div>
                <ChatInterface />
            </div>
        </div>
    );
}
