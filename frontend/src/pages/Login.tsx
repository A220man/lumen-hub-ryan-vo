/** Login page component with Keycloak/OIDC redirect. */

import { useAuth } from "../hooks/useAuth";

export function Login() {
  const { login, isLoading, error } = useAuth();

  return (
    <div className="login-page">
      <div className="card" style={{ maxWidth: "400px", margin: "2rem auto" }}>
        <h2 style={{ marginBottom: "1.5rem", textAlign: "center" }}>Sign in to Lumen Hub</h2>

        {error && <div className="alert alert-error">{error}</div>}

        <button
          className="btn btn-primary"
          style={{ width: "100%", padding: "0.75rem" }}
          onClick={login}
          disabled={isLoading}
        >
          {isLoading ? "Redirecting to Keycloak..." : "Sign in with Keycloak"}
        </button>

        <p style={{ marginTop: "1rem", textAlign: "center", color: "#718096", fontSize: "0.875rem" }}>
          If not redirected, <a href="#" onClick={login}>click here</a>
        </p>
      </div>
    </div>
  );
}
