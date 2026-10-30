import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { ProtectedRoute } from "./components/ProtectedRoute";

function AppRoutes() {
  const { handleCallback, isLoading } = useAuth();

  // Handle OAuth callback
  if (window.location.search.includes("code=") || window.location.search.includes("error=")) {
    handleCallback();
    return <div className="loading"><div className="spinner" /></div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <div className="app">
        <header className="app-header">
          <h1>Lumen Hub</h1>
          <nav>
            <a href="/">Dashboard</a>
          </nav>
        </header>
        <main className="app-main">
          <AppRoutes />
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
