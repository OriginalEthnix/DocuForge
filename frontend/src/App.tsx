import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'sonner';
import { useAuthStore } from '@/store/auth.store';
import { Sidebar } from '@/components/shared/Sidebar';

// Pages
import { LoginPage, RegisterPage } from '@/pages/auth/AuthPages';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { ProjectsPage } from '@/pages/projects/ProjectsPage';
import { CreateProjectPage } from '@/pages/projects/CreateProjectPage';
import { ProjectDetailPage } from '@/pages/projects/ProjectDetailPage';
import { RequirementsPage } from '@/pages/generation/RequirementsPage';
import { UserStoriesPage } from '@/pages/generation/UserStoriesPage';
import {
  SRSPage, UMLPage, DFDPage, DatabasePage,
  PlanningPage, EstimationPage, RiskPage, TestCasesPage,
  TraceabilityPage, MetricsPage, MaintenancePage,
} from '@/pages/generation/GenerationPages';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

// ─── Protected Route ──────────────────────────────────────────────────────────
function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-base)',
        flexDirection: 'column',
        gap: '1rem',
      }}>
        <div style={{
          width: 48,
          height: 48,
          borderRadius: 'var(--radius-md)',
          background: 'var(--gradient-brand)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: 'pulse-glow 2s ease-in-out infinite',
        }}>
          <span style={{ fontSize: '1.5rem' }}>⚡</span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Loading DocuForge AI...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content scroll-area">
        <Outlet />
      </div>
    </div>
  );
}

// ─── Public Route (redirect if authed) ────────────────────────────────────────
function PublicRoute() {
  const { isAuthenticated } = useAuthStore();
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

// ─── App Initializer ──────────────────────────────────────────────────────────
function AppInitializer() {
  const { initAuth } = useAuthStore();
  useEffect(() => { initAuth(); }, []);
  return null;
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppInitializer />
        <Toaster
          theme="dark"
          position="top-right"
          toastOptions={{
            style: {
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-default)',
              color: 'var(--text-primary)',
            },
          }}
        />
        <Routes>
          {/* Public routes */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/new" element={<CreateProjectPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />

            {/* Generation modules */}
            <Route path="/projects/:projectId/requirements" element={<RequirementsPage />} />
            <Route path="/projects/:projectId/user-stories" element={<UserStoriesPage />} />
            <Route path="/projects/:projectId/srs" element={<SRSPage />} />
            <Route path="/projects/:projectId/diagrams/uml" element={<UMLPage />} />
            <Route path="/projects/:projectId/diagrams/dfd" element={<DFDPage />} />
            <Route path="/projects/:projectId/database" element={<DatabasePage />} />
            <Route path="/projects/:projectId/planning" element={<PlanningPage />} />
            <Route path="/projects/:projectId/estimation" element={<EstimationPage />} />
            <Route path="/projects/:projectId/risks" element={<RiskPage />} />
            <Route path="/projects/:projectId/tests" element={<TestCasesPage />} />
            <Route path="/projects/:projectId/traceability" element={<TraceabilityPage />} />
            <Route path="/projects/:projectId/metrics" element={<MetricsPage />} />
            <Route path="/projects/:projectId/maintenance" element={<MaintenancePage />} />
          </Route>

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
