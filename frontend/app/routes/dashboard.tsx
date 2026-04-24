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
  return (
    <main className="shell">
      <section className="card">
        <p className="eyebrow">Dashboard</p>
        <h1>Docassist</h1>
        <p className="lede">
          This route is the placeholder for authenticated application work in the React Router
          stack.
        </p>
      </section>
    </main>
  );
}
