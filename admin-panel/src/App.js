import { Routes, Route, Navigate } from "react-router-dom";
import AdminLogin from "./components/Login/Login";
import Dashboard from "./components/Dashboard/Dashboard";

function RequireAdminAuth({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/" replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<AdminLogin />} />
      <Route path="/dashboard" element={
        <RequireAdminAuth>
          <Dashboard />
        </RequireAdminAuth>
      } />
    </Routes>
  );
}

export default App;
