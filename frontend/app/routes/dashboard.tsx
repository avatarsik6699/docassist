import { DashboardPage } from "@pages/dashboard/ui/dashboard-page";

export function meta() {
  return [
    { title: "Docassist Dashboard" },
    {
      name: "description",
      content: "Protected dashboard placeholder for Docassist.",
    },
  ];
}

export default function DashboardRoute() {
  return <DashboardPage />;
}
