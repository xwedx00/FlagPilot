import { createFileRoute } from "@tanstack/react-router";
import { LoginForm } from "~/components/login-form";

export const Route = createFileRoute("/(auth-pages)/login")({
  component: LoginPage,
});

function LoginPage() {
  const { redirectUrl } = Route.useRouteContext();

  return <LoginForm redirectUrl={redirectUrl} />;
}
