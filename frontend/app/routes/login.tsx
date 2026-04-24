import { LoginPage } from "@pages/login/ui/login-page";

export function meta() {
  return [
    { title: "Docassist Login" },
    {
      name: "description",
      content: "Authentication entry route for Docassist.",
    },
  ];
}

export default function LoginRoute() {
  return <LoginPage />;
}
