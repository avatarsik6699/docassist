import { api } from "@shared/api/client";

export async function loader() {
  const { data, error } = await api.get("/api/v1/auth/me");
  if (error) throw new Response("Unauthorized", { status: 401 });
  return data; // typed from the generated schema
}

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
