import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { ShaderRipple } from "~/components/shader-ripple";
import { authQueryOptions } from "~/lib/auth/queries";

export const Route = createFileRoute("/(auth-pages)")({
  component: RouteComponent,
  beforeLoad: async ({ context }) => {
    const REDIRECT_URL = "/dashboard";

    const user = await context.queryClient.ensureQueryData({
      ...authQueryOptions(),
      revalidateIfStale: true,
    });
    if (user) {
      throw redirect({
        to: REDIRECT_URL,
      });
    }

    return {
      redirectUrl: REDIRECT_URL,
    };
  },
});

function RouteComponent() {
  return (
    <div className="h-screen flex items-center justify-center relative">
      <div className="w-full z-10 relative max-w-sm p-6">
        <Outlet />
      </div>
      <ShaderRipple className="absolute -z-0 inset-0 h-screen" />
    </div>
  );
}
