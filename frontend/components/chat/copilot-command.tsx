"use client";

import * as React from "react";
import { useEffect, useRef, useCallback } from "react";
import gsap from "gsap";
import {
    Command,
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from "@/components/ui/command";
import {
    FileText,
    Shield,
    AlertTriangle,
    DollarSign,
    MessageSquare,
    Users,
    Zap,
    Brain,
    Search,
    Settings,
    Download,
    Trash2,
    Moon,
    Sun,
} from "lucide-react";

interface CopilotCommandProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onCommand?: (command: string, args?: Record<string, any>) => void;
}

const AGENT_COMMANDS = [
    {
        id: "analyze-contract",
        label: "Analyze Contract",
        icon: FileText,
        shortcut: "⌘C",
        description: "Review a contract for risks and unfair terms",
    },
    {
        id: "detect-scam",
        label: "Detect Scam",
        icon: AlertTriangle,
        shortcut: "⌘S",
        description: "Check a job posting or message for scam patterns",
    },
    {
        id: "payment-advice",
        label: "Payment Advice",
        icon: DollarSign,
        shortcut: "⌘P",
        description: "Get help with payment issues or invoices",
    },
    {
        id: "negotiate-rate",
        label: "Negotiate Rate",
        icon: Zap,
        shortcut: "⌘N",
        description: "Get negotiation strategies for better rates",
    },
    {
        id: "draft-message",
        label: "Draft Message",
        icon: MessageSquare,
        shortcut: "⌘M",
        description: "Write professional client communications",
    },
    {
        id: "analyze-profile",
        label: "Analyze Client",
        icon: Users,
        shortcut: "⌘A",
        description: "Research and vet a potential client",
    },
];

const UI_COMMANDS = [
    {
        id: "toggle-memory",
        label: "Toggle Memory Panel",
        icon: Brain,
        description: "Show/hide the memory and wisdom panel",
    },
    {
        id: "search-knowledge",
        label: "Search Knowledge Base",
        icon: Search,
        description: "Search freelance best practices",
    },
    {
        id: "export-chat",
        label: "Export Chat",
        icon: Download,
        description: "Download conversation history",
    },
    {
        id: "clear-chat",
        label: "Clear Chat",
        icon: Trash2,
        description: "Start a fresh conversation",
    },
];

export function CopilotCommand({ open, onOpenChange, onCommand }: CopilotCommandProps) {
    const listRef = useRef<HTMLDivElement>(null);

    // GSAP stagger animation when dialog opens
    useEffect(() => {
        if (open && listRef.current) {
            const items = listRef.current.querySelectorAll("[cmdk-item]");
            gsap.fromTo(
                items,
                { opacity: 0, x: -20 },
                {
                    opacity: 1,
                    x: 0,
                    duration: 0.3,
                    stagger: 0.05,
                    ease: "power2.out",
                }
            );
        }
    }, [open]);

    const handleSelect = useCallback(
        (commandId: string) => {
            onCommand?.(commandId);
            onOpenChange(false);
        },
        [onCommand, onOpenChange]
    );

    // Keyboard shortcut to open command palette
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                onOpenChange(!open);
            }
        };

        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, [open, onOpenChange]);

    return (
        <CommandDialog
            open={open}
            onOpenChange={onOpenChange}
            title="FlagPilot Command Palette"
            description="Quick access to agents and actions"
            className="max-w-lg"
        >
            <CommandInput placeholder="Type a command or search agents..." />
            <CommandList ref={listRef}>
                <CommandEmpty>No results found.</CommandEmpty>

                {/* Agent Commands */}
                <CommandGroup heading="🛡️ Protection Agents">
                    {AGENT_COMMANDS.map((cmd) => (
                        <CommandItem
                            key={cmd.id}
                            value={cmd.label}
                            onSelect={() => handleSelect(cmd.id)}
                            className="group cursor-pointer"
                        >
                            <div className="flex items-center gap-3 w-full">
                                <div className="flex items-center justify-center w-8 h-8 rounded-md bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-500/20 dark:to-purple-500/20 group-hover:from-indigo-500/20 group-hover:to-purple-500/30 transition-colors">
                                    <cmd.icon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                                </div>
                                <div className="flex flex-col flex-1 min-w-0">
                                    <span className="text-sm font-medium">{cmd.label}</span>
                                    <span className="text-xs text-zinc-500 dark:text-zinc-400 truncate">
                                        {cmd.description}
                                    </span>
                                </div>
                                <CommandShortcut>{cmd.shortcut}</CommandShortcut>
                            </div>
                        </CommandItem>
                    ))}
                </CommandGroup>

                <CommandSeparator />

                {/* UI Commands */}
                <CommandGroup heading="⚡ Quick Actions">
                    {UI_COMMANDS.map((cmd) => (
                        <CommandItem
                            key={cmd.id}
                            value={cmd.label}
                            onSelect={() => handleSelect(cmd.id)}
                            className="group cursor-pointer"
                        >
                            <div className="flex items-center gap-3 w-full">
                                <div className="flex items-center justify-center w-8 h-8 rounded-md bg-zinc-100 dark:bg-zinc-800 group-hover:bg-zinc-200 dark:group-hover:bg-zinc-700 transition-colors">
                                    <cmd.icon className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                                </div>
                                <div className="flex flex-col flex-1 min-w-0">
                                    <span className="text-sm font-medium">{cmd.label}</span>
                                    <span className="text-xs text-zinc-500 dark:text-zinc-400 truncate">
                                        {cmd.description}
                                    </span>
                                </div>
                            </div>
                        </CommandItem>
                    ))}
                </CommandGroup>
            </CommandList>

            {/* Footer */}
            <div className="flex items-center justify-between px-3 py-2 border-t border-zinc-200 dark:border-zinc-800 text-xs text-zinc-500">
                <span>
                    Press <kbd className="px-1.5 py-0.5 bg-zinc-100 dark:bg-zinc-800 rounded">⌘K</kbd> to toggle
                </span>
                <span className="flex items-center gap-1">
                    <Shield className="w-3 h-3" /> FlagPilot
                </span>
            </div>
        </CommandDialog>
    );
}

export default CopilotCommand;
