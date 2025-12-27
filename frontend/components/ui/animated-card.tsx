"use client";

import * as React from "react";
import { useLayoutEffect, useRef } from "react";
import { gsap } from "gsap";
import { cn } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

/**
 * AnimatedCard - Card with GSAP entrance animation
 * Wraps Shadcn Card with premium micro-interactions
 */
interface AnimatedCardProps extends React.ComponentProps<typeof Card> {
    delay?: number;
    duration?: number;
    animateOnce?: boolean;
}

export function AnimatedCard({
    delay = 0,
    duration = 0.5,
    animateOnce = true,
    className,
    children,
    ...props
}: AnimatedCardProps) {
    const cardRef = useRef<HTMLDivElement>(null);
    const hasAnimated = useRef(false);

    useLayoutEffect(() => {
        if (!cardRef.current) return;
        if (animateOnce && hasAnimated.current) return;

        const ctx = gsap.context(() => {
            gsap.fromTo(
                cardRef.current,
                {
                    opacity: 0,
                    y: 20,
                    scale: 0.98,
                },
                {
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    duration,
                    delay,
                    ease: "power3.out",
                }
            );
        }, cardRef);

        hasAnimated.current = true;
        return () => ctx.revert();
    }, [delay, duration, animateOnce]);

    // Hover effect
    useLayoutEffect(() => {
        if (!cardRef.current) return;

        const el = cardRef.current;

        const onEnter = () => {
            gsap.to(el, {
                y: -2,
                boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
                duration: 0.2,
                ease: "power2.out"
            });
        };

        const onLeave = () => {
            gsap.to(el, {
                y: 0,
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                duration: 0.2,
                ease: "power2.out"
            });
        };

        el.addEventListener("mouseenter", onEnter);
        el.addEventListener("mouseleave", onLeave);

        return () => {
            el.removeEventListener("mouseenter", onEnter);
            el.removeEventListener("mouseleave", onLeave);
        };
    }, []);

    return (
        <Card
            ref={cardRef}
            className={cn("will-change-transform", className)}
            {...props}
        >
            {children}
        </Card>
    );
}

/**
 * Staggered card list animation
 * Animates a container's children with staggered timing
 */
interface StaggeredListProps extends React.ComponentProps<"div"> {
    staggerDelay?: number;
    itemSelector?: string;
}

export function StaggeredList({
    staggerDelay = 0.08,
    itemSelector = "> *",
    className,
    children,
    ...props
}: StaggeredListProps) {
    const listRef = useRef<HTMLDivElement>(null);

    useLayoutEffect(() => {
        if (!listRef.current) return;

        const ctx = gsap.context(() => {
            gsap.fromTo(
                listRef.current!.querySelectorAll(itemSelector),
                { opacity: 0, y: 15 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.4,
                    stagger: staggerDelay,
                    ease: "power2.out"
                }
            );
        }, listRef);

        return () => ctx.revert();
    }, [staggerDelay, itemSelector]);

    return (
        <div ref={listRef} className={className} {...props}>
            {children}
        </div>
    );
}

// Re-export card parts for convenience
export { CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
