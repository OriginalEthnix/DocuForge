import React from 'react';
import { NavLink, useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, FolderOpen, Plus, Zap, LogOut, Settings,
  ChevronRight, FileText, GitBranch, Database, BarChart3,
  Shield, TestTube, Network, Activity, Clock, Wrench,
  Layers, Link2, TrendingUp, BookOpen, Code2, Map,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';

const mainNav = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/projects', icon: FolderOpen, label: 'Projects' },
];

const projectModules = [
  { path: 'requirements', icon: FileText, label: 'Requirements', color: '#818cf8' },
  { path: 'user-stories', icon: BookOpen, label: 'User Stories', color: '#34d399' },
  { path: 'srs', icon: Layers, label: 'SRS Document', color: '#60a5fa' },
  { path: 'diagrams/uml', icon: GitBranch, label: 'UML Diagrams', color: '#f472b6' },
  { path: 'diagrams/dfd', icon: Network, label: 'DFD Diagrams', color: '#fb923c' },
  { path: 'database', icon: Database, label: 'Database Design', color: '#a78bfa' },
  { path: 'planning', icon: Map, label: 'Project Planning', color: '#4ade80' },
  { path: 'estimation', icon: TrendingUp, label: 'Estimation', color: '#fbbf24' },
  { path: 'risks', icon: Shield, label: 'Risk Management', color: '#f87171' },
  { path: 'tests', icon: TestTube, label: 'Test Cases', color: '#38bdf8' },
  { path: 'traceability', icon: Link2, label: 'Traceability', color: '#c084fc' },
  { path: 'metrics', icon: BarChart3, label: 'Quality Metrics', color: '#86efac' },
  { path: 'maintenance', icon: Wrench, label: 'Maintenance', color: '#fcd34d' },
];

interface SidebarProps {
  collapsed?: boolean;
}

export function Sidebar({ collapsed = false }: SidebarProps) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [showProjectMenu, setShowProjectMenu] = React.useState(!!projectId);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      style={{
        width: collapsed ? 64 : 260,
        minWidth: collapsed ? 64 : 260,
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-default)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        transition: 'width 0.3s ease',
        overflow: 'hidden',
        zIndex: 100,
      }}
    >
      {/* Logo */}
      <div style={{
        padding: '1.25rem 1rem',
        borderBottom: '1px solid var(--border-default)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        minHeight: 64,
      }}>
        <div style={{
          width: 36,
          height: 36,
          borderRadius: 'var(--radius-md)',
          background: 'var(--gradient-brand)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: 'var(--shadow-brand)',
        }}>
          <Zap size={20} color="white" />
        </div>
        {!collapsed && (
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', letterSpacing: '-0.02em' }}>
              DocuForge AI
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
              SE DOCUMENTATION
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 0.625rem' }}>
        {/* Main nav */}
        <div style={{ marginBottom: '1.5rem' }}>
          {!collapsed && (
            <div style={{
              fontSize: '0.65rem',
              fontWeight: 700,
              letterSpacing: '0.1em',
              color: 'var(--text-disabled)',
              textTransform: 'uppercase',
              padding: '0 0.25rem',
              marginBottom: '0.375rem',
            }}>
              Navigation
            </div>
          )}
          {mainNav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
              style={{ marginBottom: 2 }}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}

          {/* New Project button */}
          <button
            className="sidebar-item btn-primary"
            style={{
              width: '100%',
              marginTop: '0.5rem',
              background: 'var(--gradient-brand)',
              color: 'white',
              border: 'none',
            }}
            onClick={() => navigate('/projects/new')}
          >
            <Plus size={18} style={{ flexShrink: 0 }} />
            {!collapsed && <span>New Project</span>}
          </button>
        </div>

        {/* Project modules (shown when in a project) */}
        <AnimatePresence>
          {projectId && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              style={{ marginBottom: '1.5rem' }}
            >
              {!collapsed && (
                <div style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  color: 'var(--text-disabled)',
                  textTransform: 'uppercase',
                  padding: '0 0.25rem',
                  marginBottom: '0.375rem',
                }}>
                  Generate Docs
                </div>
              )}
              {projectModules.map(({ path, icon: Icon, label, color }) => (
                <NavLink
                  key={path}
                  to={`/projects/${projectId}/${path}`}
                  className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
                  style={{ marginBottom: 2 }}
                >
                  <Icon size={16} style={{ flexShrink: 0, color }} />
                  {!collapsed && <span style={{ fontSize: '0.8rem' }}>{label}</span>}
                </NavLink>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* User Profile */}
      <div style={{
        padding: '0.75rem 0.625rem',
        borderTop: '1px solid var(--border-default)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '0.625rem',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-hover)',
        }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            background: 'var(--gradient-brand)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.75rem',
            fontWeight: 700,
            color: 'white',
            flexShrink: 0,
          }}>
            {initials}
          </div>
          {!collapsed && (
            <>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {user?.full_name}
                </div>
                <div style={{
                  fontSize: '0.7rem',
                  color: 'var(--text-muted)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {user?.email}
                </div>
              </div>
              <button
                className="btn btn-ghost btn-icon"
                onClick={handleLogout}
                title="Logout"
                style={{ padding: '0.35rem' }}
              >
                <LogOut size={15} />
              </button>
            </>
          )}
        </div>
      </div>
    </motion.aside>
  );
}
