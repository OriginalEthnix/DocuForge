import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  FolderOpen, TrendingUp, CheckCircle2, Clock, Plus,
  BarChart2, Zap, ArrowRight, FileText, Activity,
} from 'lucide-react';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import { projectService } from '@/services/project.service';
import { Project, MODULE_LABELS } from '@/types';
import { useAuthStore } from '@/store/auth.store';
import { CardSkeleton, ProgressRing, StatusBadge } from '@/components/shared';
import { formatDistanceToNow } from 'date-fns';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: [0.4, 0, 0.2, 1] as [number, number, number, number],

     },
  }),
};

export function DashboardPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: projectService.getDashboardStats,
    refetchInterval: 30000,
  });

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const statCards = [
    {
      label: 'Total Projects',
      value: stats?.total_projects ?? 0,
      icon: FolderOpen,
      color: '#818cf8',
      bg: 'rgba(99,102,241,0.1)',
      change: null,
    },
    {
      label: 'In Progress',
      value: stats?.in_progress_projects ?? 0,
      icon: Activity,
      color: '#38bdf8',
      bg: 'rgba(14,165,233,0.1)',
    },
    {
      label: 'Completed',
      value: stats?.completed_projects ?? 0,
      icon: CheckCircle2,
      color: '#4ade80',
      bg: 'rgba(34,197,94,0.1)',
    },
    {
      label: 'Docs Generated',
      value: stats?.total_documents_generated ?? 0,
      icon: FileText,
      color: '#c084fc',
      bg: 'rgba(168,85,247,0.1)',
    },
  ];

  // Chart data
  const doughnutData = {
    labels: ['Completed', 'In Progress', 'Draft'],
    datasets: [{
      data: [
        stats?.completed_projects ?? 0,
        stats?.in_progress_projects ?? 0,
        stats?.draft_projects ?? 0,
      ],
      backgroundColor: ['rgba(74,222,128,0.8)', 'rgba(56,189,248,0.8)', 'rgba(161,161,170,0.4)'],
      borderColor: ['#4ade80', '#38bdf8', '#71717a'],
      borderWidth: 1,
    }],
  };

  const moduleData = React.useMemo(() => {
    if (!stats?.module_popularity) return null;
    const entries = Object.entries(stats.module_popularity).slice(0, 8);
    return {
      labels: entries.map(([k]) => MODULE_LABELS[k] || k),
      datasets: [{
        label: 'Times Generated',
        data: entries.map(([, v]) => v),
        backgroundColor: 'rgba(99,102,241,0.7)',
        borderColor: '#6366f1',
        borderWidth: 1,
        borderRadius: 6,
      }],
    };
  }, [stats?.module_popularity]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#a1a1aa', font: { family: 'Inter', size: 12 } },
      },
      tooltip: {
        backgroundColor: '#18181b',
        borderColor: '#27272a',
        borderWidth: 1,
        titleColor: '#fafafa',
        bodyColor: '#a1a1aa',
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#71717a', font: { size: 11 } },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#71717a', font: { size: 11 } },
      },
    },
  };

  return (
    <div className="page-container">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '2rem' }}
      >
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.03em' }}>
          {greeting()},{' '}
          <span className="gradient-text">{user?.full_name?.split(' ')[0]}</span> 👋
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Here's what's happening with your projects today.
        </p>
      </motion.div>

      {/* Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem',
        marginBottom: '1.5rem',
      }}>
        {statCards.map((card, i) => (
          <motion.div
            key={card.label}
            className="card"
            custom={i}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            style={{ padding: '1.25rem' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500, marginBottom: '0.5rem' }}>
                  {card.label}
                </p>
                <p style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1 }}>
                  {isLoading ? '—' : card.value}
                </p>
              </div>
              <div style={{
                width: 44,
                height: 44,
                borderRadius: 'var(--radius-md)',
                background: card.bg,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: card.color,
              }}>
                <card.icon size={22} />
              </div>
            </div>
            {stats?.completion_rate !== undefined && card.label === 'Completed' && (
              <div style={{ marginTop: '0.75rem' }}>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${stats.completion_rate}%` }} />
                </div>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  {stats.completion_rate}% completion rate
                </p>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* Recent Projects */}
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{ gridColumn: 'span 2', padding: '1.5rem' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Recent Projects</h2>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/projects')}>
              View all <ArrowRight size={14} />
            </button>
          </div>

          {isLoading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {[1, 2, 3].map(i => <CardSkeleton key={i} />)}
            </div>
          ) : stats?.recent_projects?.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              <FolderOpen size={32} style={{ marginBottom: '0.5rem', opacity: 0.4 }} />
              <p>No projects yet. Create your first one!</p>
              <button className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }} onClick={() => navigate('/projects/new')}>
                <Plus size={14} /> Create Project
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {stats?.recent_projects?.map((project) => (
                <ProjectRow key={project.id} project={project} onClick={() => navigate(`/projects/${project.id}`)} />
              ))}
            </div>
          )}
        </motion.div>

        {/* Doughnut Chart */}
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          style={{ padding: '1.5rem' }}
        >
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1.25rem' }}>Project Status</h2>
          {stats?.total_projects === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              <BarChart2 size={32} style={{ marginBottom: '0.5rem', opacity: 0.4 }} />
              <p style={{ fontSize: '0.8rem' }}>No data yet</p>
            </div>
          ) : (
            <>
              <div style={{ position: 'relative', height: 180 }}>
                <Doughnut
                  data={doughnutData}
                  options={{
                    ...chartOptions,
                    plugins: {
                      ...chartOptions.plugins,
                      legend: {
                        position: 'bottom',
                        labels: { color: '#a1a1aa', font: { family: 'Inter', size: 11 }, padding: 16, boxWidth: 12 },
                      },
                    },
                    cutout: '65%',
                  }}
                />
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -60%)',
                  textAlign: 'center',
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{stats?.total_projects}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PROJECTS</div>
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>

      {/* Module Popularity Chart */}
      {moduleData && Object.keys(stats?.module_popularity || {}).length > 0 && (
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          style={{ padding: '1.5rem' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Zap size={18} style={{ color: 'var(--color-brand-400)' }} />
            <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Most Used Modules</h2>
          </div>
          <div style={{ height: 200 }}>
            <Bar data={moduleData} options={chartOptions} />
          </div>
        </motion.div>
      )}

      {/* Quick Start Banner */}
      {stats?.total_projects === 0 && !isLoading && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          style={{
            background: 'var(--gradient-brand-soft)',
            border: '1px solid var(--border-brand)',
            borderRadius: 'var(--radius-xl)',
            padding: '2.5rem',
            textAlign: 'center',
            marginTop: '1rem',
          }}
        >
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🚀</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Welcome to DocuForge AI!
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', maxWidth: 480, margin: '0 auto 1.5rem' }}>
            Create your first project and let AI generate complete IEEE-standard software engineering documentation in minutes.
          </p>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/projects/new')}>
            <Plus size={18} /> Create Your First Project
          </button>
        </motion.div>
      )}
    </div>
  );
}

function ProjectRow({ project, onClick }: { project: Project; onClick: () => void }) {
  const modulesCount = project.generated_modules?.length || 0;
  return (
    <motion.div
      whileHover={{ backgroundColor: 'var(--bg-hover)', x: 2 }}
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem',
        borderRadius: 'var(--radius-md)',
        cursor: 'pointer',
        transition: 'all var(--transition-fast)',
        border: '1px solid transparent',
      }}
    >
      <ProgressRing percentage={project.completion_percentage} size={40} strokeWidth={4} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {project.title}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {modulesCount}/13 modules • {project.domain}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
        <StatusBadge status={project.status} />
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {project.updated_at || project.created_at
            ? formatDistanceToNow(new Date(project.updated_at || project.created_at), { addSuffix: true })
            : ''}
        </span>
      </div>
    </motion.div>
  );
}
