import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import Assessment from "./pages/Assessment";
import Practice from "./pages/Practice";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import Navbar from "./components/Navbar";

// Protected Route Component
function ProtectedRoute({ children, role }: { children: React.ReactNode, role?: "student" | "teacher" }) {
  const { user, loading } = useAuth();
  
  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (role && user.role !== role) return <Navigate to="/" />;
  
  return <>{children}</>;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen selection:bg-blue-500/30">
      <Navbar />
      <main className="container mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={user ? (user.role === 'teacher' ? <Navigate to="/teacher" /> : <Navigate to="/student" />) : <LandingPage />} />
          <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          
          <Route path="/student" element={
            <ProtectedRoute role="student">
              <StudentDashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/assessment/:subjectId" element={
            <ProtectedRoute role="student">
              <Assessment />
            </ProtectedRoute>
          } />
          
          <Route path="/practice/:topicId" element={
            <ProtectedRoute role="student">
              <Practice />
            </ProtectedRoute>
          } />

          <Route path="/teacher" element={
            <ProtectedRoute role="teacher">
              <TeacherDashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
