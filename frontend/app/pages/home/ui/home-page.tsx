export function HomePage() {
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
