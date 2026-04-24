export function meta() {
  return [
    { title: "Docassist" },
    {
      name: "description",
      content: "Docassist built on FastAPI and React Router SSR.",
    },
    {
      tagName: "link",
      rel: "canonical",
      href: "https://example.com/",
    },
  ];
}

export default function HomeRoute() {
  return (
    <main className="shell">
      <div className="hero">
        <p className="eyebrow">SSR Reference Stack</p>
        <h1>Docassist</h1>
        <p className="lede">
          FastAPI handles the API surface. React Router handles SSR, routing, and SEO metadata.
        </p>
        <a className="cta" href="/login">
          Open login route
        </a>
      </div>
    </main>
  );
}
