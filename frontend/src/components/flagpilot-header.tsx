"use client";

import * as React from "react";
import { Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Shield, Rocket, Menu, X } from "lucide-react";
import { Button } from "~/components/ui/button";
import { ThemeToggle } from "~/components/theme-toggle";
import { cn } from "~/lib/utils";

interface FlagPilotHeaderProps {
    className?: string;
}

export function FlagPilotHeader({ className }: FlagPilotHeaderProps) {
    const [scrolled, setScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 0);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <header
            className={cn(
                `sticky top-0 z-50 w-full transition-all duration-300`,
                scrolled ? "bg-background/80 backdrop-blur-xl border-b shadow-sm" : "bg-transparent",
                className
            )}
        >
            <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg group-hover:shadow-violet-500/25 transition-all duration-300 group-hover:scale-105">
                        <Shield className="h-5 w-5 text-white" />
                    </div>
                    <span className="font-bold text-xl hidden sm:inline tracking-tight">FlagPilot</span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center gap-1">
                    <a
                        href="#features"
                        className="rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                        Features
                    </a>
                    <a
                        href="#pricing"
                        className="rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                        Pricing
                    </a>
                    <a
                        href="https://github.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-full px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                    >
                        Docs
                    </a>
                </nav>

                {/* Right Actions */}
                <div className="flex items-center gap-2">
                    <ThemeToggle />
                    <Button
                        variant="ghost"
                        size="sm"
                        asChild
                        className="hidden sm:inline-flex rounded-full"
                    >
                        <Link to="/login">Sign In</Link>
                    </Button>
                    <Button
                        size="sm"
                        asChild
                        className="rounded-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-violet-500/25 transition-all"
                    >
                        <Link to="/login">
                            <Rocket className="h-4 w-4 mr-1" />
                            Get Started
                        </Link>
                    </Button>

                    {/* Mobile Menu Toggle */}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="md:hidden"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                    </Button>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t bg-background/95 backdrop-blur-xl">
                    <nav className="container mx-auto flex flex-col gap-2 p-4">
                        <a
                            href="#features"
                            className="rounded-lg px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
                            onClick={() => setMobileMenuOpen(false)}
                        >
                            Features
                        </a>
                        <a
                            href="#pricing"
                            className="rounded-lg px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
                            onClick={() => setMobileMenuOpen(false)}
                        >
                            Pricing
                        </a>
                        <a
                            href="https://github.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="rounded-lg px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
                        >
                            Docs
                        </a>
                    </nav>
                </div>
            )}
        </header>
    );
}
