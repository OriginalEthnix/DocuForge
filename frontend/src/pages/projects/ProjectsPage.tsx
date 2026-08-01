import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Plus, FolderOpen, Search, Trash2, ArrowRight, Calendar,
  Users, Clock, Code2, ChevronDown,
} from 'lucide-react';
import { projectService } from '@/services/project.service';
import { Project } from '@/types';
import { StatusBadge, ProgressRing, EmptyState, CardSkeleton } from '@/components/shared';
import { formatDistanceToNow } from 'date-fns';
import { getErrorMessage } from '@/services/api';

const DOMAIN_COLORS: Record<string, string> = {
  web: '#818cf8', mobile: '#34d399', desktop: '#60a5fa',
  ai_ml: '#f472b6', fintech: '#fbbf24', healthcare: '#4ade80',
  ecommerce: '#fb923c', education: '#a78bfa', embedded: '#38bdf8', other: '#a1a1aa',
};

export function ProjectsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['projects', statusFilter],
    queryFn: () => projectService.list(1, 50, statusFilter || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: projectService.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  });

  const filtered = React.useMemo(() => {
    if (!data?.projects) return [];
    return data.projects.filter(p =>
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.domain.toLowerCase().includes(search.toLowerCase())
    );
  }, [data?.projects, search]);

  return (
    <div className="page-container">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}
      >
        <div>
          <h1 style={{ fontSize: '1.625rem', fontWeight: 700, letterSpacing: '-0.02em' }}>Projects</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 2 }}>
            {data?.total ?? 0} projects total
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/projects/new')}>
          <Plus size={16} /> New Project
        </button>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}
      >
        <div style={{ position: 'relative', flex: '1 1 200px', minWidth: 0 }}>
          <Search size={15} style={{
            position: 'absolute', left: '0.75rem', top: '50%',
            transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none',
          }} />
          <input
            className="input-field"
            style={{ paddingLeft: '2.5rem' }}
            placeholder="Search projects..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input-field"
          style={{ width: 'auto', paddingRight: '2rem', flexShrink: 0 }}
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
      </motion.div>

      {/* Grid */}
      {isLoading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem' }}>
          {[1,2,3,4,5,6].map(i => <CardSkeleton key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<FolderOpen size={32} />}
          title={search ? 'No projects match your search' : 'No projects yet'}
          description={search ? 'Try a different search term.' : 'Create your first project to start generating AI-powered documentation.'}
          action={
            !search && (
              <button className="btn btn-primary" onClick={() => navigate('/projects/new')}>
                <Plus size={16} /> Create Project
              </button>
            )
          }
        />
      ) : (
        <motion.div
          layout
          style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem' }}
        >
          <AnimatePresence>
            {filtered.map((project, i) => (
              <ProjectCard
                key={project.id}
                project={project}
                index={i}
                onClick={() => navigate(`/projects/${project.id}`)}
                onDelete={() => {
                  if (confirm(`Delete "${project.title}"? This cannot be undone.`)) {
                    deleteMutation.mutate(project.id);
                  }
                }}
              />
            ))}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
}

function ProjectCard({
  project, index, onClick, onDelete,
}: {
  project: Project;
  index: number;
  onClick: () => void;
  onDelete: () => void;
}) {
  const [showDelete, setShowDelete] = React.useState(false);
  const domainColor = DOMAIN_COLORS[project.domain] || '#a1a1aa';
  const modulesCount = project.generated_modules?.length || 0;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ delay: index * 0.04, duration: 0.3 }}
      className="card"
      style={{
        padding: '1.25rem',
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
      }}
      whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.4)' }}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
      onClick={onClick}
    >
      {/* Domain accent bar */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0,
        height: 3,
        background: domainColor,
        borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0',
        opacity: 0.8,
      }} />

      {/* Delete button */}
      <AnimatePresence>
        {showDelete && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="btn btn-danger btn-icon"
            style={{ position: 'absolute', top: '0.75rem', right: '0.75rem', zIndex: 10 }}
            onClick={e => { e.stopPropagation(); onDelete(); }}
          >
            <Trash2 size={13} />
          </motion.button>
        )}
      </AnimatePresence>

      <div style={{ marginTop: '0.5rem' }}>
        {/* Status + Domain */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <span className="badge" style={{ background: `${domainColor}20`, color: domainColor, fontSize: '0.7rem' }}>
            {project.domain.toUpperCase()}
          </span>
          <StatusBadge status={project.status} />
        </div>

        {/* Title */}
        <h3 style={{
          fontSize: '1rem',
          fontWeight: 700,
          marginBottom: '0.375rem',
          letterSpacing: '-0.01em',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}>
          {project.title}
        </h3>
        <p style={{
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
          marginBottom: '1rem',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          lineHeight: 1.5,
        }}>
          {project.description}
        </p>

        {/* Progress */}
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {modulesCount}/13 modules
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: domainColor }}>
              {project.completion_percentage}%
            </span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${project.completion_percentage}%`, background: domainColor }} />
          </div>
        </div>

        {/* Meta */}
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Users size={13} /> {project.team_size}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Clock size={13} /> {project.timeline_weeks}w
          </span>
          {project.tech_stack?.length > 0 && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Code2 size={13} /> {project.tech_stack.slice(0, 2).join(', ')}{project.tech_stack.length > 2 ? '...' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Open button */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        marginTop: '0.875rem',
        paddingTop: '0.875rem',
        borderTop: '1px solid var(--border-subtle)',
        gap: '0.5rem',
      }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {project.updated_at || project.created_at
            ? formatDistanceToNow(new Date(project.updated_at || project.created_at), { addSuffix: true })
            : ''}
        </span>
        <button className="btn btn-ghost btn-sm" style={{ color: 'var(--color-brand-400)', padding: '0.3rem 0.6rem' }}>
          Open <ArrowRight size={13} />
        </button>
      </div>
    </motion.div>
  );
}
