import { Routes, Route } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { ProtectedRoute } from "./components/ProtectedRoute";

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Lumen Hub</h1>
        <nav>
          <a href="/">Dashboard</a>
        </nav>
      </header>
      <main className="app-main">
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
        </Routes>
      </main>
    </div>
  );
}

export default App;