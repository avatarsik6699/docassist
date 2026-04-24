export function LoginPage() {
  return (
    <main className="shell shell-narrow">
      <section className="card">
        <p className="eyebrow">Login</p>
        <h1>Docassist</h1>
        <form className="form">
          <label>
            Email
            <input name="email" type="email" autoComplete="email" />
          </label>
          <label>
            Password
            <input name="password" type="password" autoComplete="current-password" />
          </label>
          <button type="submit">Continue</button>
        </form>
      </section>
    </main>
  );
}
