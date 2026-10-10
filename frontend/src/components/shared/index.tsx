import React from 'react';
import { motion } from 'framer-motion';
import { Download, Loader2, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react';
import { generationService, downloadFileFromUrl } from '@/services/generation.service';
import { getErrorMessage } from '@/services/api';

interface GenerateButtonProps {
  projectId: number;
  module: string;
  onSuccess?: (data: any) => void;
  label?: string;
  disabled?: boolean;
}

export function GenerateButton({
  projectId,
  module,
  onSuccess,
  label = 'Generate with AI',
  disabled = false,
}: GenerateButtonProps) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);

  const generate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      let data: any;
      const svc = generationService as any;
      const methodMap: Record<string, string> = {
        requirements: 'generateRequirements',
        user_stories: 'generateUserStories',
        srs: 'generateSRS',
        uml: 'generateUML',
        dfd: 'generateDFD',
        database: 'generateDatabase',
        planning: 'generatePlanning',
        estimation: 'generateEstimation',
        risks: 'generateRisks',
        tests: 'generateTestCases',
        traceability: 'generateTraceability',
        metrics: 'generateMetrics',
        maintenance: 'generateMaintenance',
      };
      const method = methodMap[module];
      if (method && svc[method]) {
        data = await svc[method](projectId);
      }
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      onSuccess?.(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <motion.button
        className="btn btn-primary"
        onClick={generate}
        disabled={loading || disabled}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {loading ? (
          <>
            <Loader2 size={16} style={{ animation: 'spin-slow 0.6s linear infinite' }} />
            Generating...
          </>
        ) : success ? (
          <>
            <CheckCircle2 size={16} />
            Generated!
          </>
        ) : (
          <>
            <Sparkles size={16} />
            {label}
          </>
        )}
      </motion.button>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.5rem',
            padding: '0.625rem 0.875rem',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.2)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.8rem',
            color: '#f87171',
          }}
        >
          <AlertCircle size={14} style={{ flexShrink: 0, marginTop: 1 }} />
          {error}
        </motion.div>
      )}
    </div>
  );
}

// ─── Loading Skeleton ─────────────────────────────────────────────────────────

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
}

export function Skeleton({ width = '100%', height = 20, borderRadius }: SkeletonProps) {
  return (
    <div
      className="skeleton"
      style={{
        width,
        height,
        borderRadius: borderRadius || 'var(--radius-md)',
      }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <Skeleton height={20} width="60%" />
      <Skeleton height={14} width="80%" />
      <Skeleton height={14} width="70%" />
      <Skeleton height={14} width="50%" />
    </div>
  );
}

// ─── Empty State ──────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 2rem',
        textAlign: 'center',
        gap: '1rem',
      }}
    >
      {icon && (
        <div style={{
          width: 72,
          height: 72,
          borderRadius: '50%',
          background: 'rgba(99,102,241,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-brand-400)',
          marginBottom: '0.5rem',
        }}>
          {icon}
        </div>
      )}
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h3>
      {description && (
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '0.875rem',
          maxWidth: 360,
          lineHeight: 1.6,
        }}>
          {description}
        </p>
      )}
      {action}
    </motion.div>
  );
}

// ─── Status Badge ─────────────────────────────────────────────────────────────

const statusMap: Record<string, { label: string; cls: string }> = {
  draft: { label: 'Draft', cls: 'badge-neutral' },
  in_progress: { label: 'In Progress', cls: 'badge-info' },
  completed: { label: 'Completed', cls: 'badge-success' },
  archived: { label: 'Archived', cls: 'badge-neutral' },
  open: { label: 'Open', cls: 'badge-warning' },
  mitigated: { label: 'Mitigated', cls: 'badge-success' },
  closed: { label: 'Closed', cls: 'badge-neutral' },
  critical: { label: 'Critical', cls: 'badge-error' },
  high: { label: 'High', cls: 'badge-error' },
  medium: { label: 'Medium', cls: 'badge-warning' },
  low: { label: 'Low', cls: 'badge-success' },
};

export function StatusBadge({ status }: { status: string }) {
  const info = statusMap[status?.toLowerCase()] || { label: status, cls: 'badge-neutral' };
  return <span className={`badge ${info.cls}`}>{info.label}</span>;
}

// ─── Section Header ───────────────────────────────────────────────────────────

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export function SectionHeader({ title, subtitle, action, icon }: SectionHeaderProps) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      marginBottom: '1.5rem',
      gap: '1rem',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {icon && (
          <div style={{
            width: 40,
            height: 40,
            borderRadius: 'var(--radius-md)',
            background: 'rgba(99,102,241,0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-brand-400)',
          }}>
            {icon}
          </div>
        )}
        <div>
          <h1 style={{ fontSize: '1.375rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            {title}
          </h1>
          {subtitle && (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 2 }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// ─── Progress Ring ────────────────────────────────────────────────────────────

interface ProgressRingProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
}

export function ProgressRing({
  percentage,
  size = 80,
  strokeWidth = 6,
  color = '#6366f1',
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--bg-hover)"
        strokeWidth={strokeWidth}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
      />
    </svg>
  );
}

// ─── PDF Export Button ────────────────────────────────────────────────────────

export function ExportPDFButton({ projectId }: { projectId: number }) {
  const [loading, setLoading] = React.useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const result = await generationService.exportPDF(projectId);
      downloadFileFromUrl(result.download_url, result.filename);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('PDF export failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button className="btn btn-secondary" onClick={handleExport} disabled={loading}>
      {loading ? <Loader2 size={16} /> : <Download size={16} />}
      {loading ? 'Exporting...' : 'Export PDF'}
    </button>
  );
}