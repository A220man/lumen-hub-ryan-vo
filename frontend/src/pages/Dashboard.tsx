/** Dashboard page component. */

import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import type { HealthResponse } from "../types";

export function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch("/api/v1/health");
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        setHealth(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch health");
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="dashboard">
      <div style={{ marginBottom: "2rem" }}>
        <h1>Welcome, {user?.name || user?.email || "User"}</h1>
        <p style={{ color: "#718096" }}>Lumen Hub - AI/ML Developer Platform</p>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: "1rem" }}>Service Health</h2>
        
        {loading && <div className="loading"><div className="spinner" /></div>}
        
        {error && <div className="alert alert-error">{error}</div>}
        
        {health && (
          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
            <div style={{ padding: "1rem", background: "#f0fff4", borderRadius: "0.375rem" }}>
              <strong>Status:</strong> <span style={{ color: "#276749" }}>{health.status}</span>
            </div>
            <div style={{ padding: "1rem", background: "#ebf8ff", borderRadius: "0.375rem" }}>
              <strong>Service:</strong> {health.service}
            </div>
            <div style={{ padding: "1rem", background: "#faf5ff", borderRadius: "0.375rem" }}>
              <strong>Version:</strong> {health.version}
            </div>
            <div style={{ padding: "1rem", background: "#fffaf0", borderRadius: "0.375rem" }}>
              <strong>Environment:</strong> {health.environment}
            </div>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h2 style={{ marginBottom: "1rem" }}>Quick Actions</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <button className="btn btn-primary">Manage SMS Templates</button>
          <button className="btn btn-secondary">Project Health</button>
          <button className="btn btn-secondary">SMTP Settings</button>
        </div>
      </div>
    </div>
  );
}