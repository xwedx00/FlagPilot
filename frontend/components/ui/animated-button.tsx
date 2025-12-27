"use client";

import * as React from "react";
import { useLayoutEffect, useRef } from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { gsap } from "gsap";
import { cn } from "@/lib/utils";

/**
 * AnimatedButton - Button with GSAP micro-interactions
 * Provides premium feel with spring-physics hover and click animations
 */

const animatedButtonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 will-change-transform",
    {
        variants: {
            variant: {
                default: "bg-primary text-primary-foreground shadow-md hover:bg-primary/90",
                destructive: "bg-destructive text-white shadow-md hover:bg-destructive/90",
                outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
                secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
                ghost: "hover:bg-accent hover:text-accent-foreground",
                link: "text-primary underline-offset-4 hover:underline",
                // Premium variants
                gradient: "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg hover:shadow-xl hover:from-indigo-600 hover:to-purple-700",
                glow: "bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40",
            },
            size: {
                default: "h-10 px-4 py-2",
                sm: "h-9 rounded-md px-3",
                lg: "h-11 rounded-md px-8",
                xl: "h-12 rounded-lg px-10 text-base",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
);

interface AnimatedButtonProps
    extends React.ComponentProps<"button">,
    VariantProps<typeof animatedButtonVariants> {
    asChild?: boolean;
    disableAnimation?: boolean;
}

export function AnimatedButton({
    className,
    variant,
    size,
    asChild = false,
    disableAnimation = false,
    ...props
}: AnimatedButtonProps) {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const Comp = asChild ? Slot : "button";

    useLayoutEffect(() => {
        if (!buttonRef.current || disableAnimation) return;

        const el = buttonRef.current;

        const onEnter = () => {
            gsap.to(el, {
                scale: 1.02,
                duration: 0.2,
                ease: "power2.out",
            });
        };

        const onLeave = () => {
            gsap.to(el, {
                scale: 1,
                duration: 0.2,
                ease: "power2.out",
            });
        };

        const onDown = () => {
            gsap.to(el, {
                scale: 0.98,
                duration: 0.1,
                ease: "power2.out",
            });
        };

        const onUp = () => {
            gsap.to(el, {
                scale: 1.02,
                duration: 0.15,
                ease: "back.out(2)",
            });
        };

        el.addEventListener("mouseenter", onEnter);
        el.addEventListener("mouseleave", onLeave);
        el.addEventListener("mousedown", onDown);
        el.addEventListener("mouseup", onUp);

        return () => {
            el.removeEventListener("mouseenter", onEnter);
            el.removeEventListener("mouseleave", onLeave);
            el.removeEventListener("mousedown", onDown);
            el.removeEventListener("mouseup", onUp);
        };
    }, [disableAnimation]);

    return (
        <Comp
            ref={buttonRef}
            className={cn(animatedButtonVariants({ variant, size, className }))}
            {...props}
        />
    );
}

export { animatedButtonVariants };
