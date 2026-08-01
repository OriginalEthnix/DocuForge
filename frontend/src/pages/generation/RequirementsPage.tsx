/**
 * Requirements Analysis Page
 */
import React from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { FileText, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import { generationService } from '@/services/generation.service';
import { GenerateButton, SectionHeader, StatusBadge, EmptyState, CardSkeleton } from '@/components/shared';

const PRIORITY_COLORS: Record<string, string> = {
  high: '#f87171', medium: '#fbbf24', low: '#4ade80',
};

export function RequirementsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['requirements', id],
    queryFn: () => generationService.getRequirements(id),
  });

  const hasData = data && (
    (data.functional?.length > 0) ||
    (data.non_functional?.length > 0) ||
    (data.business?.length > 0)
  );

  const totalCount = (data?.functional?.length || 0) + (data?.non_functional?.length || 0) + (data?.business?.length || 0);

  return (
    <div className="page-container">
      <SectionHeader
        title="Requirements Analysis"
        subtitle="AI-generated IEEE 830 compliant requirements specification"
        icon={<FileText size={20} />}
        action={
          <GenerateButton
            projectId={id}
            module="requirements"
            label="Generate Requirements"
            onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['requirements', id] }); refetch(); }}
          />
        }
      />

      {/* Stats */}
      {hasData && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}
        >
          {[
            { label: 'Functional', count: data.functional?.length || 0, color: '#818cf8', icon: CheckCircle },
            { label: 'Non-Functional', count: data.non_functional?.length || 0, color: '#38bdf8', icon: TrendingUp },
            { label: 'Business', count: data.business?.length || 0, color: '#4ade80', icon: AlertCircle },
            { label: 'Total', count: totalCount, color: '#c084fc', icon: FileText },
          ].map(stat => (
            <div key={stat.label} className="card" style={{ flex: '1 1 140px', padding: '1rem', textAlign: 'center' }}>
              <stat.icon size={20} style={{ color: stat.color, marginBottom: '0.375rem' }} />
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: stat.color }}>{stat.count}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stat.label}</div>
            </div>
          ))}
        </motion.div>
      )}

      {isLoading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[1,2,3].map(i => <CardSkeleton key={i} />)}
        </div>
      ) : !hasData ? (
        <EmptyState
          icon={<FileText size={32} />}
          title="No requirements generated yet"
          description="Click 'Generate Requirements' to create a comprehensive IEEE 830 requirements specification powered by AI."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Functional Requirements */}
          {data.functional?.length > 0 && (
            <ReqSection
              title="Functional Requirements"
              items={data.functional}
              color="#818cf8"
              badge="badge-brand"
            />
          )}

          {/* Non-Functional Requirements */}
          {data.non_functional?.length > 0 && (
            <ReqSection
              title="Non-Functional Requirements"
              items={data.non_functional}
              color="#38bdf8"
              badge="badge-info"
            />
          )}

          {/* Business Requirements */}
          {data.business?.length > 0 && (
            <ReqSection
              title="Business Requirements"
              items={data.business}
              color="#4ade80"
              badge="badge-success"
            />
          )}

          {/* Stakeholders + Assumptions */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            {data.stakeholders?.length > 0 && (
              <InfoSection title="Stakeholders" items={data.stakeholders} color="#f472b6" />
            )}
            {data.assumptions?.length > 0 && (
              <InfoSection title="Assumptions" items={data.assumptions} color="#fbbf24" />
            )}
            {data.constraints?.length > 0 && (
              <InfoSection title="Constraints" items={data.constraints} color="#f87171" />
            )}
            {data.dependencies?.length > 0 && (
              <InfoSection title="Dependencies" items={data.dependencies} color="#a78bfa" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ReqSection({ title, items, color, badge }: { title: string; items: any[]; color: string; badge: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.875rem', color, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ display: 'inline-block', width: 4, height: 18, background: color, borderRadius: 2 }} />
        {title} ({items.length})
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {items.map((req: any, i: number) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.03 }}
            className="card"
            style={{ padding: '1rem', borderLeft: `3px solid ${color}` }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem', marginBottom: '0.375rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color, fontWeight: 700 }}>{req.req_id}</span>
                <span className={`badge ${badge}`} style={{ fontSize: '0.65rem' }}>{req.category}</span>
              </div>
              <span style={{ fontSize: '0.7rem', fontWeight: 600, color: PRIORITY_COLORS[req.priority] || '#a1a1aa' }}>
                {req.priority?.toUpperCase()}
              </span>
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>{req.title}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{req.description}</div>
            {req.acceptance_criteria && (
              <div style={{
                marginTop: '0.625rem',
                padding: '0.5rem 0.75rem',
                background: 'var(--bg-overlay)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                borderLeft: '2px solid var(--border-strong)',
              }}>
                <strong style={{ color: 'var(--text-secondary)' }}>Acceptance:</strong> {req.acceptance_criteria}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

function InfoSection({ title, items, color }: { title: string; items: string[]; color: string }) {
  return (
    <div className="card" style={{ padding: '1rem' }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color, marginBottom: '0.75rem' }}>{title}</h3>
      <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
        {items.map((item, i) => (
          <li key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
            <span style={{ color, marginTop: 4, flexShrink: 0 }}>•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
