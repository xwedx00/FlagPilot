import { PageHeader } from "@/components/layout/page-header"
import { ChatInterface } from "@/components/chat-interface"
import type { Metadata } from "next"

export const metadata: Metadata = {
    title: "Dashboard"
}

export default function DashboardPage() {
    return (
        <div className="flex flex-col h-full">
            <PageHeader
                title="Hi, Welcome back 👋"
                description="Here's what's happening with your account today."
            />
            <div className="flex-1 mt-4">
                <ChatInterface />
            </div>
        </div>
    )
}