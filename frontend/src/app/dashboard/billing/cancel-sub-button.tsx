"use client";

import { authClient } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CancelSubscription() {
	const router = useRouter();
	const [isPending, setIsPending] = useState(false);

	async function handleManageSubscription() {
		try {
			setIsPending(true);
			const loadingToast = toast.loading("Redirecting to customer portal...");


			const result = await authClient.customer.portal();

			// If the method returns a url rather than redirecting automatically (depending on implementation), we might need to handle it.
			// But usually it redirects. If it returns data, we check it.
			if (result?.data?.url) {
				router.push(result.data.url);
			}

			toast.dismiss(loadingToast);
		} catch (error) {
			console.log(error);
			toast.error("Failed to redirect to portal");
			setIsPending(false);
		}
	}

	return (
		<Button
			variant="outline"
			onClick={handleManageSubscription}
			disabled={isPending}
		>
			{isPending ? "Redirecting..." : "Manage Subscription"}
		</Button>
	);
}