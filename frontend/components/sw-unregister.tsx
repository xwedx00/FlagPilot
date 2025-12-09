"use client";

import { useEffect } from "react";

export function SwUnregister() {
    useEffect(() => {
        if (typeof window !== "undefined" && "serviceWorker" in navigator) {
            navigator.serviceWorker.getRegistrations().then((registrations) => {
                for (const registration of registrations) {
                    registration.unregister();
                    console.log("Unregistered Service Worker:", registration);
                }
            });
        }
    }, []);

    return null;
}
