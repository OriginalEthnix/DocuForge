import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft, Download, Clock, Users, Code2, Globe,
  CheckCircle2, Circle, Sparkles, ExternalLink,
  FileText, BookOpen, Layers, GitBranch, Network,
  Database, Map, TrendingUp, Shield, TestTube,
  Link2, BarChart3, Wrench, Upload, Loader2, AlertCircle, Paperclip,
} from 'lucide-react';
import { projectService } from '@/services/project.service';
import { MODULE_LABELS, ALL_MODULES } from '@/types';
import { StatusBadge, ProgressRing, ExportPDFButton, CardSkeleton } from '@/components/shared';
import { generationService, downloadFileFromUrl } from '@/services/generation.service';
import { getErrorMessage } from '@/services/api';
import { formatDistanceToNow } from 'date-fns';


const MODULE_ICONS: Record<string, any> = {
  requirements: FileText,
  user_stories: BookOpen,
  srs: Layers,
  uml_diagrams: GitBranch,
  dfd_diagrams: Network,
  database_design: Database,
  planning: Map,
  estimation: TrendingUp,
  risks: Shield,
  test_cases: TestTube,
  traceability: Link2,
  metrics: BarChart3,
  maintenance: Wrench,
};

const MODULE_ROUTES: Record<string, string> = {
  requirements: 'requirements',
  user_stories: 'user-stories',
  srs: 'srs',
  uml_diagrams: 'diagrams/uml',
  dfd_diagrams: 'diagrams/dfd',
  database_design: 'database',
  planning: 'planning',
  estimation: 'estimation',
  risks: 'risks',
  test_cases: 'tests',
  traceability: 'traceability',
  metrics: 'metrics',
  maintenance: 'maintenance',
};

const MODULE_COLORS: Record<string, string> = {
  requirements: '#818cf8', user_stories: '#34d399', srs: '#60a5fa',
  uml_diagrams: '#f472b6', dfd_diagrams: '#fb923c', database_design: '#a78bfa',
  planning: '#4ade80', estimation: '#fbbf24', risks: '#f87171',
  test_cases: '#38bdf8', traceability: '#c084fc', metrics: '#86efac',
  maintenance: '#fcd34d',
};

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const id = parseInt(projectId || '0');

  // ── File Upload State ────────────────────────────────────────────────────────
  const [uploadError, setUploadError] = React.useState<string | null>(null);
  const [uploading, setUploading] = React.useState(false);
  const [uploadedFiles, setUploadedFiles] = React.useState<Array<{
    id: number;
    filename: string;
    content_type: string;
    size_bytes: number;
    download_url: string;
    expires_in_seconds: number;
  }>>([]);
  const [downloadingId, setDownloadingId] = React.useState<number | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    // Reset the input so the same file can be re-uploaded
    e.target.value = '';

    setUploading(true);
    setUploadError(null);
    try {
      const result = await generationService.uploadFile(id, file);
      setUploadedFiles((prev) => [result, ...prev]);
    } catch (err) {
      setUploadError(getErrorMessage(err));
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (fileId: number, filename: string) => {
    setDownloadingId(fileId);
    try {
      const result = await generationService.getFileDownload(id, fileId);
      downloadFileFromUrl(result.download_url, result.filename || filename);
    } catch (err) {
      setUploadError(getErrorMessage(err));
    } finally {
      setDownloadingId(null);
    }
  };

  // ────────────────────────────────────────────────────────────────────────────

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectService.get(id),
    enabled: !!id,
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="page-container">
        <CardSkeleton />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '4rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>Project not found.</p>
        <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/projects')}>
          Back to Projects
        </button>
      </div>
    );
  }

  const generatedSet = new Set(project.generated_modules || []);

  return (
    <div className="page-container">
      {/* Back */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: '1.25rem' }}
        onClick={() => navigate('/projects')}
      >
        <ArrowLeft size={16} /> Back to Projects
      </motion.button>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'var(--gradient-card)',
          border: '1px solid var(--border-brand)',
          borderRadius: 'var(--radius-xl)',
          padding: 'clamp(1.25rem, 3vw, 1.75rem)',
          marginBottom: '1.5rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background gradient blob */}
        <div style={{
          position: 'absolute',
          top: -40,
          right: -40,
          width: 200,
          height: 200,
          background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 280px', minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
              <StatusBadge status={project.status} />
              <span className="badge badge-brand">{project.domain.toUpperCase()}</span>
            </div>
            <h1 style={{
              fontSize: 'clamp(1.35rem, 3.5vw, 1.75rem)',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              marginBottom: '0.5rem',
              wordBreak: 'break-word',
            }}>
              {project.title}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, maxWidth: 600 }}>
              {project.description}
            </p>

            {/* Meta row */}
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
              <MetaItem icon={<Users size={14} />} label={`${project.team_size} member${project.team_size !== 1 ? 's' : ''}`} />
              <MetaItem icon={<Clock size={14} />} label={`${project.timeline_weeks} weeks`} />
              {project.tech_stack?.length > 0 && (
                <MetaItem icon={<Code2 size={14} />} label={project.tech_stack.slice(0, 3).join(', ')} />
              )}
              <MetaItem icon={<Globe size={14} />} label={`Updated ${project.updated_at || project.created_at ? formatDistanceToNow(new Date(project.updated_at || project.created_at), { addSuffix: true }) : 'recently'}`} />
            </div>
          </div>

          {/* Progress ring */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', flexShrink: 0, margin: '0 auto' }}>
            <div style={{ position: 'relative' }}>
              <ProgressRing percentage={project.completion_percentage} size={88} strokeWidth={7} />
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800 }}>{project.completion_percentage}%</div>
              </div>
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              {generatedSet.size}/13 modules
            </span>
            <ExportPDFButton projectId={id} />
          </div>
        </div>
      </motion.div>

      {/* Documentation Modules Grid */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-secondary)' }}>
          📄 Documentation Modules
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 200px), 1fr))',
          gap: '0.875rem',
        }}>
          {ALL_MODULES.map((module, i) => {
            const isGenerated = generatedSet.has(module);
            const Icon = MODULE_ICONS[module] || FileText;
            const color = MODULE_COLORS[module] || '#a1a1aa';
            const route = MODULE_ROUTES[module] || module;

            return (
              <motion.div
                key={module}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => navigate(`/projects/${id}/${route}`)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                  padding: '1.125rem',
                  borderRadius: 'var(--radius-lg)',
                  border: `1px solid ${isGenerated ? `${color}40` : 'var(--border-default)'}`,
                  background: isGenerated ? `${color}08` : 'var(--bg-elevated)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  position: 'relative',
                }}
                whileHover={{
                  y: -2,
                  borderColor: `${color}60`,
                  boxShadow: `0 4px 20px ${color}20`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: 'var(--radius-md)',
                    background: `${color}20`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color,
                  }}>
                    <Icon size={18} />
                  </div>
                  {isGenerated ? (
                    <CheckCircle2 size={16} style={{ color: '#4ade80' }} />
                  ) : (
                    <Circle size={16} style={{ color: 'var(--text-disabled)' }} />
                  )}
                </div>

                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.2rem' }}>
                    {MODULE_LABELS[module]}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {isGenerated ? '✓ Generated' : 'Click to generate'}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color, fontSize: '0.72rem', fontWeight: 500 }}>
                  <Sparkles size={12} />
                  {isGenerated ? 'View & Regenerate' : 'Generate with AI'}
                  <ExternalLink size={11} />
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* ── File Upload Section ──────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        style={{
          marginTop: '2rem',
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-default)',
          borderRadius: 'var(--radius-xl)',
          padding: '1.5rem',
        }}
      >
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Paperclip size={16} /> Project Files
        </h2>

        {/* Upload trigger */}
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.625rem',
            padding: '0.75rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            border: '1px dashed var(--border-brand)',
            background: uploading ? 'rgba(99,102,241,0.05)' : 'transparent',
            cursor: uploading ? 'not-allowed' : 'pointer',
            transition: 'all var(--transition-fast)',
            fontSize: '0.875rem',
            color: 'var(--color-brand-400)',
            fontWeight: 500,
            width: 'fit-content',
          }}
        >
          {uploading ? (
            <>
              <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
              Uploading…
            </>
          ) : (
            <>
              <Upload size={15} />
              Upload a file
            </>
          )}
          <input
            type="file"
            style={{ display: 'none' }}
            disabled={uploading}
            onChange={handleFileUpload}
          />
        </label>

        {/* Upload error */}
        {uploadError && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem',
              marginTop: '0.75rem',
              padding: '0.625rem 0.875rem',
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.8rem',
              color: '#f87171',
            }}
          >
            <AlertCircle size={14} style={{ flexShrink: 0, marginTop: 1 }} />
            {uploadError}
          </motion.div>
        )}

        {/* Uploaded file list */}
        {uploadedFiles.length > 0 && (
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {uploadedFiles.map((f) => (
              <div
                key={f.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.625rem 0.875rem',
                  background: 'var(--bg-surface)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)',
                  gap: '1rem',
                  flexWrap: 'wrap',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
                  <FileText size={14} style={{ color: 'var(--color-brand-400)', flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: '0.825rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {f.filename}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {f.content_type} · {(f.size_bytes / 1024).toFixed(1)} KB
                    </div>
                  </div>
                </div>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => handleDownload(f.id, f.filename)}
                  disabled={downloadingId === f.id}
                  style={{ flexShrink: 0 }}
                >
                  {downloadingId === f.id ? (
                    <Loader2 size={13} style={{ animation: 'spin 0.8s linear infinite' }} />
                  ) : (
                    <Download size={13} />
                  )}
                  Download
                </button>
              </div>
            ))}
          </div>
        )}

        {uploadedFiles.length === 0 && !uploading && (
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
            No files uploaded yet. Upload design docs, specs, or any project assets.
          </p>
        )}
      </motion.div>
    </div>
  );
}

function MetaItem({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
      {icon}
      {label}
    </div>
  );
}
