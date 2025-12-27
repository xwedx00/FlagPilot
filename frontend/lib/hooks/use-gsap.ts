"use client";

import { useLayoutEffect, useRef } from "react";
import { gsap } from "gsap";

/**
 * GSAP Animation Hook
 * React-safe GSAP integration with automatic cleanup
 */
export function useGSAP<T extends HTMLElement = HTMLElement>(
    animation: (context: gsap.Context, element: T) => void,
    deps: React.DependencyList = []
) {
    const ref = useRef<T>(null);

    useLayoutEffect(() => {
        if (!ref.current) return;

        const ctx = gsap.context(() => {
            animation(ctx, ref.current!);
        }, ref);

        return () => ctx.revert();
    }, deps);

    return ref;
}

/**
 * Fade-in animation with scale
 */
export function useFadeIn<T extends HTMLElement = HTMLElement>(
    delay: number = 0,
    duration: number = 0.5
) {
    return useGSAP<T>((ctx, el) => {
        gsap.fromTo(el,
            { opacity: 0, y: 20, scale: 0.95 },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration,
                delay,
                ease: "power2.out"
            }
        );
    }, [delay, duration]);
}

/**
 * Stagger animation for lists
 */
export function useStaggerAnimation<T extends HTMLElement = HTMLElement>(
    selector: string = "> *",
    staggerAmount: number = 0.08
) {
    return useGSAP<T>((ctx, el) => {
        gsap.fromTo(
            el.querySelectorAll(selector),
            { opacity: 0, y: 15 },
            {
                opacity: 1,
                y: 0,
                duration: 0.4,
                stagger: staggerAmount,
                ease: "power2.out"
            }
        );
    }, [selector, staggerAmount]);
}

/**
 * Hover scale effect - call in a parent component
 */
export function applyHoverScale(element: HTMLElement, scale: number = 1.02) {
    const onEnter = () => gsap.to(element, { scale, duration: 0.2, ease: "power2.out" });
    const onLeave = () => gsap.to(element, { scale: 1, duration: 0.2, ease: "power2.out" });

    element.addEventListener("mouseenter", onEnter);
    element.addEventListener("mouseleave", onLeave);

    return () => {
        element.removeEventListener("mouseenter", onEnter);
        element.removeEventListener("mouseleave", onLeave);
    };
}

export { gsap };
