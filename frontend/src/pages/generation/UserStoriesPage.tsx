/**
 * User Stories Page — Agile Stories with sprint grouping
 */
import React from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { BookOpen, Star, Target, CheckSquare } from 'lucide-react';
import { generationService } from '@/services/generation.service';
import { GenerateButton, SectionHeader, EmptyState, CardSkeleton, DownloadArtifactButton } from '@/components/shared';

const PRIORITY_COLORS: Record<string, string> = {
  critical: '#f87171', high: '#fb923c', medium: '#fbbf24', low: '#4ade80',
};
const POINT_COLORS = [0, 1, 2, 3, 5, 8, 13];

export function UserStoriesPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const queryClient = useQueryClient();
  const [groupBy, setGroupBy] = React.useState<'sprint' | 'epic'>('sprint');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['user-stories', id],
    queryFn: () => generationService.getUserStories(id),
  });

  const stories = data?.stories || [];

  const grouped = React.useMemo(() => {
    const groups: Record<string, any[]> = {};
    stories.forEach((s: any) => {
      const key = groupBy === 'sprint' ? `Sprint ${s.sprint || 1}` : (s.epic || 'General');
      if (!groups[key]) groups[key] = [];
      groups[key].push(s);
    });
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [stories, groupBy]);

  return (
    <div className="page-container">
      <SectionHeader
        title="User Stories"
        subtitle={`${stories.length} stories • ${data?.total_story_points || 0} total story points`}
        icon={<BookOpen size={20} />}
        action={
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
              {(['sprint', 'epic'] as const).map(g => (
                <button
                  key={g}
                  className={`btn btn-sm ${groupBy === g ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ borderRadius: 0 }}
                  onClick={() => setGroupBy(g)}
                >
                  By {g.charAt(0).toUpperCase() + g.slice(1)}
                </button>
              ))}
            </div>
            <DownloadArtifactButton downloadUrl={data?.download_url} filename={`user_stories_project_${id}.json`} />
            <GenerateButton
              projectId={id}
              module="user_stories"
              label={stories.length > 0 ? "Regenerate Stories" : "Generate Stories"}
              onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['user-stories', id] }); refetch(); }}
            />
          </div>
        }
      />

      {isLoading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[1,2,3].map(i => <CardSkeleton key={i} />)}
        </div>
      ) : stories.length === 0 ? (
        <EmptyState
          icon={<BookOpen size={32} />}
          title="No user stories generated yet"
          description="Generate Agile user stories with acceptance criteria, story points, and sprint assignments."
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {grouped.map(([groupName, groupStories]) => (
            <motion.div key={groupName} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '0.875rem',
                padding: '0.5rem 0.875rem',
                background: 'rgba(99,102,241,0.08)',
                border: '1px solid var(--border-brand)',
                borderRadius: 'var(--radius-md)',
              }}>
                <Target size={16} style={{ color: 'var(--color-brand-400)' }} />
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--color-brand-400)' }}>{groupName}</span>
                <span className="badge badge-brand" style={{ fontSize: '0.7rem' }}>
                  {groupStories.length} stories • {groupStories.reduce((s: number, st: any) => s + (st.story_points || 0), 0)} pts
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '0.75rem' }}>
                {groupStories.map((story: any, i: number) => (
                  <StoryCard key={i} story={story} index={i} />
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function StoryCard({ story, index }: { story: any; index: number }) {
  const [expanded, setExpanded] = React.useState(false);
  const pColor = PRIORITY_COLORS[story.priority] || '#a1a1aa';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.04 }}
      className="card"
      style={{ padding: '1rem', cursor: 'pointer' }}
      onClick={() => setExpanded(!expanded)}
      whileHover={{ y: -1 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--color-brand-400)', fontWeight: 700 }}>{story.story_id}</span>
          <span style={{
            width: 24, height: 24,
            borderRadius: '50%',
            background: 'rgba(99,102,241,0.2)',
            color: 'var(--color-brand-400)',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.7rem', fontWeight: 700,
          }}>
            {story.story_points}
          </span>
        </div>
        <span style={{ fontSize: '0.7rem', fontWeight: 600, color: pColor }}>
          {story.priority?.toUpperCase()}
        </span>
      </div>

      <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.5rem' }}>{story.title}</div>

      <div style={{
        fontSize: '0.8rem',
        color: 'var(--text-secondary)',
        lineHeight: 1.6,
        background: 'var(--bg-overlay)',
        padding: '0.625rem',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '0.5rem',
      }}>
        <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>As a </span>
        <span style={{ color: '#818cf8' }}>{story.as_a}</span>
        <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>, I want </span>
        <span>{story.i_want}</span>
        <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>, so that </span>
        <span>{story.so_that}</span>
      </div>

      {expanded && story.acceptance_criteria?.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{ marginTop: '0.5rem' }}
        >
          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
            ACCEPTANCE CRITERIA
          </div>
          {story.acceptance_criteria.map((ac: string, i: number) => (
            <div key={i} style={{ display: 'flex', gap: '0.375rem', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem', lineHeight: 1.5 }}>
              <CheckSquare size={13} style={{ color: '#4ade80', flexShrink: 0, marginTop: 2 }} />
              {ac}
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
