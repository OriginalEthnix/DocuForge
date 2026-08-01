/**
 * Generic generation page template — used for SRS, Database, Planning, Estimation, Traceability, Metrics, Maintenance
 */
import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Layers, Database, Map, TrendingUp, Link2, BarChart3, Wrench } from 'lucide-react';
import { generationService } from '@/services/generation.service';
import { GenerateButton, SectionHeader, EmptyState, CardSkeleton } from '@/components/shared';
import { Radar, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS, RadialLinearScale, PointElement, LineElement,
  Filler, Tooltip, Legend, CategoryScale, LinearScale, BarElement
} from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const CHART_OPTIONS = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#a1a1aa', font: { family: 'Inter', size: 11 } } }, tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', borderWidth: 1, titleColor: '#fafafa', bodyColor: '#a1a1aa' } },
  scales: { r: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#71717a', backdropColor: 'transparent' }, pointLabels: { color: '#a1a1aa', font: { size: 11 } } }, x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#71717a' } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#71717a' } } },
};

// ─── SRS Page ─────────────────────────────────────────────────────────────────
export function SRSPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const { data, isLoading, refetch } = useQuery({ queryKey: ['srs', id], queryFn: () => generationService.getSRS(id) });
  const content = data?.content;

  return (
    <div className="page-container">
      <SectionHeader title="SRS Document" subtitle="IEEE 830 Software Requirements Specification" icon={<Layers size={20} />}
        action={<GenerateButton projectId={id} module="srs" label="Generate SRS" onSuccess={() => { qc.invalidateQueries({ queryKey: ['srs', id] }); refetch(); }} />} />
      {isLoading ? <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>{[1,2,3].map(i => <CardSkeleton key={i} />)}</div>
        : !content ? <EmptyState icon={<Layers size={32} />} title="SRS not generated" description="Generate a complete IEEE 830 compliant Software Requirements Specification document." />
        : <SRSContent content={content} />}
    </div>
  );
}

function SRSContent({ content }: { content: any }) {
  const sections = [
    { key: 'section_1_introduction', title: '1. Introduction' },
    { key: 'section_2_overall_description', title: '2. Overall Description' },
    { key: 'section_3_functional_requirements', title: '3. Functional Requirements' },
    { key: 'section_4_nonfunctional_requirements', title: '4. Non-Functional Requirements' },
    { key: 'section_5_external_interfaces', title: '5. External Interfaces' },
    { key: 'section_6_other_requirements', title: '6. Other Requirements' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {content.document_info && (
        <div className="card" style={{ padding: '1.25rem', background: 'var(--gradient-card)', border: '1px solid var(--border-brand)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, textAlign: 'center', marginBottom: '0.5rem' }} className="gradient-text">
            {content.document_info.title}
          </h2>
          <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <span>Version: {content.document_info.version}</span>
            <span>Date: {content.document_info.date}</span>
            <span>Status: {content.document_info.status}</span>
          </div>
        </div>
      )}
      {sections.map(({ key, title }) => content[key] ? (
        <motion.div key={key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card" style={{ padding: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-brand-400)', marginBottom: '1rem' }}>{title}</h2>
          <JsonContent data={content[key]} />
        </motion.div>
      ) : null)}
    </div>
  );
}

function JsonContent({ data }: { data: any }) {
  if (Array.isArray(data)) {
    return (
      <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {data.map((item, i) => (
          <li key={i} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--color-brand-400)', flexShrink: 0, marginTop: 2 }}>▸</span>
            {typeof item === 'object' ? (
              <div style={{ flex: 1 }}>
                {item.id && <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--color-brand-400)', marginRight: '0.5rem' }}>{item.id}</span>}
                {item.name && <strong style={{ marginRight: '0.5rem' }}>{item.name}</strong>}
                {item.description && <span style={{ color: 'var(--text-secondary)' }}>{item.description}</span>}
              </div>
            ) : (
              <span style={{ color: 'var(--text-secondary)' }}>{item}</span>
            )}
          </li>
        ))}
      </ul>
    );
  }
  if (typeof data === 'object') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
        {Object.entries(data).map(([k, v]) => (
          <div key={k} style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '0.75rem', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'capitalize', paddingTop: 2 }}>
              {k.replace(/_/g, ' ')}:
            </span>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {Array.isArray(v) ? v.join(', ') : String(v)}
            </div>
          </div>
        ))}
      </div>
    );
  }
  return <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{String(data)}</p>;
}


// ─── Diagrams Page ────────────────────────────────────────────────────────────
import { useParams as useParamsDiagram } from 'react-router-dom';
import { GitBranch, Network, Code2, Maximize2 } from 'lucide-react';

export function UMLPage() {
  return <DiagramsPage category="uml" module="uml" title="UML Diagrams" subtitle="Automatically generated PlantUML diagrams" icon={<GitBranch size={20} />} />;
}

export function DFDPage() {
  return <DiagramsPage category="dfd" module="dfd" title="DFD Diagrams" subtitle="Context, Level 0, and Level 1 Data Flow Diagrams" icon={<Network size={20} />} />;
}

function DiagramsPage({ category, module, title, subtitle, icon }: { category: string; module: string; title: string; subtitle: string; icon: React.ReactNode }) {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [selected, setSelected] = React.useState<any>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['diagrams', id, category],
    queryFn: () => generationService.getDiagrams(id, category),
  });

  const diagrams = data?.diagrams || [];

  return (
    <div className="page-container">
      <SectionHeader title={title} subtitle={subtitle} icon={icon}
        action={<GenerateButton projectId={id} module={module} label={`Generate ${title}`} onSuccess={() => { qc.invalidateQueries({ queryKey: ['diagrams', id, category] }); refetch(); }} />} />

      {isLoading ? <CardSkeleton /> : diagrams.length === 0 ? (
        <EmptyState icon={icon} title={`No ${title} generated yet`} description={`Generate ${title} from your project description using AI and PlantUML.`} />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
          {diagrams.map((diag: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="card" style={{ padding: '1rem', cursor: 'pointer' }}
              whileHover={{ y: -2 }} onClick={() => setSelected(diag)}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{diag.title}</span>
                <Maximize2 size={14} style={{ color: 'var(--text-muted)' }} />
              </div>
              {diag.svg_content ? (
                <div dangerouslySetInnerHTML={{ __html: diag.svg_content }} style={{ width: '100%', overflow: 'hidden', borderRadius: 'var(--radius-sm)', background: '#fff', minHeight: 120 }} />
              ) : (
                <div className="code-block" style={{ fontSize: '0.7rem', maxHeight: 120, overflow: 'hidden' }}>
                  {diag.plantuml_code?.split('\n').slice(0, 8).join('\n')}
                </div>
              )}
              <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: 'var(--text-muted)' }} className="badge badge-neutral">{diag.diagram_type}</div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Diagram modal */}
      {selected && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 1000, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}
          onClick={() => setSelected(null)}>
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="card" style={{ maxWidth: 900, width: '100%', padding: '1.5rem' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h2 style={{ fontWeight: 700 }}>{selected.title}</h2>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>✕ Close</button>
            </div>
            {selected.svg_content ? (
              <div dangerouslySetInnerHTML={{ __html: selected.svg_content }} style={{ background: '#fff', padding: '1rem', borderRadius: 'var(--radius-md)', overflow: 'auto', maxHeight: '70vh' }} />
            ) : (
              <pre className="code-block" style={{ whiteSpace: 'pre-wrap', maxHeight: '70vh', overflow: 'auto' }}>
                {selected.plantuml_code}
              </pre>
            )}
            <div style={{ marginTop: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>PlantUML Source:</div>
              <pre className="code-block" style={{ maxHeight: 160, overflow: 'auto', fontSize: '0.75rem' }}>{selected.plantuml_code}</pre>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}


// ─── Database Design Page ─────────────────────────────────────────────────────
export function DatabasePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<'entities' | 'er' | 'sql'>('entities');

  const { data, isLoading, refetch } = useQuery({ queryKey: ['database', id], queryFn: () => generationService.getDatabase(id) });
  const content = data?.content;

  return (
    <div className="page-container">
      <SectionHeader title="Database Design" subtitle="Entities, relationships, ER diagram, and SQL schema" icon={<Database size={20} />}
        action={<GenerateButton projectId={id} module="database" label="Generate DB Design" onSuccess={() => { qc.invalidateQueries({ queryKey: ['database', id] }); refetch(); }} />} />

      {isLoading ? <CardSkeleton /> : !content ? (
        <EmptyState icon={<Database size={32} />} title="Database design not generated" description="Generate normalized database tables with relationships, ER diagram, and SQL schema." />
      ) : (
        <>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-default)', paddingBottom: '0.5rem' }}>
            {[['entities', 'Entities'], ['er', 'ER Diagram'], ['sql', 'SQL Schema']].map(([t, l]) => (
              <button key={t} className={`btn btn-sm ${activeTab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab(t as any)}>{l}</button>
            ))}
          </div>

          {activeTab === 'entities' && content.entities?.map((entity: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="card" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#818cf8', marginBottom: '0.25rem' }}>{entity.name}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.875rem' }}>{entity.description}</p>
              <table className="data-table">
                <thead><tr><th>Field</th><th>Type</th><th>Constraints</th><th>Description</th></tr></thead>
                <tbody>{entity.fields?.map((f: any, j: number) => (
                  <tr key={j}>
                    <td style={{ fontFamily: 'monospace', color: '#818cf8', fontSize: '0.8rem' }}>{f.name}</td>
                    <td><span className="badge badge-info" style={{ fontSize: '0.65rem' }}>{f.data_type}</span></td>
                    <td style={{ fontSize: '0.75rem' }}>{f.constraints?.join(', ')}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{f.description}</td>
                  </tr>
                ))}</tbody>
              </table>
            </motion.div>
          ))}

          {activeTab === 'er' && (
            content.er_diagram_svg ? (
              <div dangerouslySetInnerHTML={{ __html: content.er_diagram_svg }} style={{ background: '#fff', padding: '2rem', borderRadius: 'var(--radius-lg)', overflow: 'auto' }} />
            ) : content.er_diagram_plantuml ? (
              <pre className="code-block">{content.er_diagram_plantuml}</pre>
            ) : <p style={{ color: 'var(--text-muted)' }}>ER Diagram not available</p>
          )}

          {activeTab === 'sql' && content.sql_schema && (
            <pre className="code-block" style={{ maxHeight: '70vh', overflow: 'auto', whiteSpace: 'pre-wrap' }}>{content.sql_schema}</pre>
          )}
        </>
      )}
    </div>
  );
}


// ─── Risk Management Page ─────────────────────────────────────────────────────
import { Shield, AlertTriangle, ChevronDown } from 'lucide-react';
import { StatusBadge } from '@/components/shared';

const RISK_LEVEL_STYLES: Record<string, string> = {
  critical: 'badge-error', high: 'badge-error', medium: 'badge-warning', low: 'badge-success',
};

export function RiskPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [expanded, setExpanded] = React.useState<number | null>(null);

  const { data, isLoading, refetch } = useQuery({ queryKey: ['risks', id], queryFn: () => generationService.getRisks(id) });
  const risks = data?.risks || [];

  const riskCounts = risks.reduce((acc: any, r: any) => { acc[r.risk_level] = (acc[r.risk_level] || 0) + 1; return acc; }, {});

  return (
    <div className="page-container">
      <SectionHeader title="Risk Management" subtitle={`${risks.length} risks identified and analyzed`} icon={<Shield size={20} />}
        action={<GenerateButton projectId={id} module="risks" label="Generate Risk Register" onSuccess={() => { qc.invalidateQueries({ queryKey: ['risks', id] }); refetch(); }} />} />

      {risks.length > 0 && (
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {[['critical', '#f87171', 'Critical'], ['high', '#fb923c', 'High'], ['medium', '#fbbf24', 'Medium'], ['low', '#4ade80', 'Low']].map(([level, color, label]) => (
            riskCounts[level] ? (
              <div key={level} className="card" style={{ flex: '1 1 100px', padding: '0.875rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color }}>{riskCounts[level]}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{label}</div>
              </div>
            ) : null
          ))}
        </div>
      )}

      {isLoading ? <CardSkeleton /> : risks.length === 0 ? (
        <EmptyState icon={<Shield size={32} />} title="No risks analyzed" description="Generate a comprehensive risk register with probability, impact, mitigation strategies and risk matrix." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
          {risks.map((risk: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
              className="card" style={{ padding: '1rem', cursor: 'pointer' }} onClick={() => setExpanded(expanded === i ? null : i)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--color-brand-400)', fontWeight: 700, flexShrink: 0 }}>{risk.risk_id}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{risk.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{risk.category} • Owner: {risk.owner}</div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexShrink: 0 }}>
                  <span className={`badge ${RISK_LEVEL_STYLES[risk.risk_level] || 'badge-neutral'}`}>{risk.risk_level?.toUpperCase()}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>P:{risk.probability?.toUpperCase()} × I:{risk.impact?.toUpperCase()}</span>
                  <ChevronDown size={16} style={{ color: 'var(--text-muted)', transform: expanded === i ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                </div>
              </div>
              {expanded === i && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ marginTop: '0.875rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <InfoBox title="Description" content={risk.description} color="#f87171" />
                  <InfoBox title="Mitigation Strategy" content={risk.mitigation_strategy} color="#4ade80" />
                  {risk.contingency_plan && <InfoBox title="Contingency Plan" content={risk.contingency_plan} color="#fbbf24" />}
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function InfoBox({ title, content, color }: { title: string; content: string; color: string }) {
  return (
    <div style={{ background: 'var(--bg-overlay)', borderRadius: 'var(--radius-md)', padding: '0.75rem', borderLeft: `3px solid ${color}` }}>
      <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.375rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{title}</div>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{content}</p>
    </div>
  );
}


// ─── Test Cases Page ──────────────────────────────────────────────────────────
import { TestTube, ChevronDown as CD2, CheckSquare as CS2 } from 'lucide-react';

export function TestCasesPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [typeFilter, setTypeFilter] = React.useState('all');
  const [expanded, setExpanded] = React.useState<number | null>(null);

  const { data, isLoading, refetch } = useQuery({ queryKey: ['tests', id], queryFn: () => generationService.getTestCases(id) });
  const allTests = data?.test_cases || [];
  const filtered = typeFilter === 'all' ? allTests : allTests.filter((t: any) => t.test_type === typeFilter);
  const types = [...new Set(allTests.map((t: any) => t.test_type as string))];

  const TYPE_COLORS: Record<string, string> = { unit: '#818cf8', integration: '#38bdf8', system: '#4ade80', acceptance: '#fbbf24', regression: '#f472b6', boundary: '#fb923c' };

  return (
    <div className="page-container">
      <SectionHeader title="Test Cases" subtitle={`${allTests.length} test cases across ${types.length} types`} icon={<TestTube size={20} />}
        action={<GenerateButton projectId={id} module="tests" label="Generate Test Cases" onSuccess={() => { qc.invalidateQueries({ queryKey: ['tests', id] }); refetch(); }} />} />

      {types.length > 0 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <button className={`btn btn-sm ${typeFilter === 'all' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTypeFilter('all')}>All ({allTests.length})</button>
          {types.map(type => (
            <button key={type} className={`btn btn-sm ${typeFilter === type ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTypeFilter(type)}
              style={typeFilter === type ? {} : { borderColor: TYPE_COLORS[type], color: TYPE_COLORS[type] }}>
              {type.charAt(0).toUpperCase() + type.slice(1)} ({allTests.filter((t: any) => t.test_type === type).length})
            </button>
          ))}
        </div>
      )}

      {isLoading ? <CardSkeleton /> : allTests.length === 0 ? (
        <EmptyState icon={<TestTube size={32} />} title="No test cases generated" description="Generate comprehensive test cases covering unit, integration, system, acceptance, boundary, and regression tests." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {filtered.map((tc: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
              className="card" style={{ padding: '1rem', cursor: 'pointer' }} onClick={() => setExpanded(expanded === i ? null : i)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: '#38bdf8', fontWeight: 700, flexShrink: 0 }}>{tc.test_id}</span>
                <span className="badge" style={{ background: `${TYPE_COLORS[tc.test_type] || '#a1a1aa'}20`, color: TYPE_COLORS[tc.test_type] || '#a1a1aa', fontSize: '0.68rem' }}>
                  {tc.test_type?.toUpperCase()}
                </span>
                <div style={{ flex: 1, fontWeight: 600, fontSize: '0.875rem' }}>{tc.title}</div>
                <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                  {tc.requirement_id && <span className="badge badge-brand" style={{ fontSize: '0.65rem' }}>{tc.requirement_id}</span>}
                  <StatusBadge status={tc.priority} />
                  <CD2 size={16} style={{ color: 'var(--text-muted)', transform: expanded === i ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                </div>
              </div>
              {expanded === i && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ marginTop: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                  {tc.preconditions && <InfoBox title="Preconditions" content={tc.preconditions} color="#a78bfa" />}
                  {tc.test_steps?.length > 0 && (
                    <div style={{ background: 'var(--bg-overlay)', borderRadius: 'var(--radius-md)', padding: '0.75rem', borderLeft: '3px solid #38bdf8' }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.375rem', textTransform: 'uppercase' }}>Test Steps</div>
                      {tc.test_steps.map((step: string, j: number) => (
                        <div key={j} style={{ display: 'flex', gap: '0.375rem', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                          <span style={{ color: '#38bdf8', fontWeight: 700, flexShrink: 0 }}>{j + 1}.</span> {step}
                        </div>
                      ))}
                    </div>
                  )}
                  <InfoBox title="Expected Result" content={tc.expected_result} color="#4ade80" />
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}


// ─── Planning Page ────────────────────────────────────────────────────────────
import { Bar as BarChart } from 'react-chartjs-2';

export function PlanningPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<'sprints' | 'gantt' | 'pert' | 'releases'>('sprints');

  const { data, isLoading, refetch } = useQuery({ queryKey: ['planning', id], queryFn: () => generationService.getPlanning(id) });
  const content = data?.content;

  return (
    <div className="page-container">
      <SectionHeader title="Project Planning" subtitle="Sprints, Gantt chart, PERT analysis, and release plan" icon={<Map size={20} />}
        action={<GenerateButton projectId={id} module="planning" label="Generate Plan" onSuccess={() => { qc.invalidateQueries({ queryKey: ['planning', id] }); refetch(); }} />} />

      {content && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-default)', paddingBottom: '0.5rem' }}>
          {[['sprints', 'Sprint Plan'], ['gantt', 'Gantt Chart'], ['pert', 'PERT'], ['releases', 'Releases']].map(([t, l]) => (
            <button key={t} className={`btn btn-sm ${activeTab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab(t as any)}>{l}</button>
          ))}
        </div>
      )}

      {isLoading ? <CardSkeleton /> : !content ? (
        <EmptyState icon={<Map size={32} />} title="No project plan generated" description="Generate a complete Agile project plan including sprints, Gantt chart, PERT analysis, and release plan." />
      ) : (
        <>
          {activeTab === 'sprints' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {content.sprints?.map((sprint: any, i: number) => (
                <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="card" style={{ padding: '1.25rem', borderLeft: '3px solid var(--color-brand-500)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--color-brand-400)' }}>Sprint {sprint.sprint_number}</div>
                    <span className="badge badge-neutral">{sprint.duration_weeks} weeks</span>
                  </div>
                  <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)', marginBottom: '0.75rem', fontSize: '0.875rem' }}>"{sprint.sprint_goal}"</div>
                  {sprint.milestones?.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {sprint.milestones.map((m: string, j: number) => <span key={j} className="badge badge-success" style={{ fontSize: '0.7rem' }}>✓ {m}</span>)}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'gantt' && content.gantt_data?.length > 0 && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ marginBottom: '1rem', fontWeight: 600 }}>Gantt Chart — Week Timeline</h3>
              <div style={{ height: 300 }}>
                <BarChart
                  data={{
                    labels: content.gantt_data.map((t: any) => t.task?.slice(0, 20)),
                    datasets: [
                      { label: 'Duration (weeks)', data: content.gantt_data.map((t: any) => t.end_week - t.start_week + 1), backgroundColor: 'rgba(99,102,241,0.7)', borderRadius: 4 },
                    ],
                  }}
                  options={{ ...CHART_OPTIONS, indexAxis: 'y' as const, plugins: { ...CHART_OPTIONS.plugins, legend: { display: false } } }}
                />
              </div>
            </div>
          )}

          {activeTab === 'pert' && content.pert_data && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ marginBottom: '1rem', fontWeight: 600 }}>PERT Analysis</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ background: 'var(--bg-overlay)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Project Duration</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#818cf8' }}>{content.pert_data.project_duration_days} days</div>
                </div>
                {content.pert_data.critical_path?.length > 0 && (
                  <div style={{ background: 'var(--bg-overlay)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Critical Path</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                      {content.pert_data.critical_path.map((node: string, i: number) => (
                        <React.Fragment key={i}><span className="badge badge-error">{node}</span>{i < content.pert_data.critical_path.length - 1 && <span style={{ color: 'var(--text-muted)' }}>→</span>}</React.Fragment>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {content.pert_data.nodes?.length > 0 && (
                <table className="data-table"><thead><tr><th>Task</th><th>Duration</th><th>Earliest Start</th><th>Latest Start</th><th>Slack</th></tr></thead>
                  <tbody>{content.pert_data.nodes.map((n: any, i: number) => (
                    <tr key={i}><td>{n.task}</td><td>{n.duration_days}d</td><td>Day {n.earliest_start}</td><td>Day {n.latest_start}</td>
                      <td><span className={`badge ${n.slack === 0 ? 'badge-error' : 'badge-success'}`}>{n.slack}d</span></td></tr>
                  ))}</tbody>
                </table>
              )}
            </div>
          )}

          {activeTab === 'releases' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {content.release_plan?.map((rel: any, i: number) => (
                <div key={i} className="card" style={{ padding: '1.25rem', borderLeft: '3px solid #4ade80' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, color: '#4ade80' }}>{rel.release}</span>
                    <span className="badge badge-neutral">Week {rel.target_week}</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginBottom: '0.5rem' }}>
                    {rel.features?.map((f: string, j: number) => <span key={j} className="badge badge-success" style={{ fontSize: '0.7rem' }}>✓ {f}</span>)}
                  </div>
                  {rel.release_criteria && <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>DoD: {rel.release_criteria}</p>}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}


// ─── Estimation Page ──────────────────────────────────────────────────────────
export function EstimationPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();
  const [tab, setTab] = React.useState<'cocomo' | 'fp' | 'cost' | 'team'>('cocomo');

  const { data, isLoading, refetch } = useQuery({ queryKey: ['estimation', id], queryFn: () => generationService.getEstimation(id) });
  const content = data?.content;

  const renderKV = (obj: any, color = '#818cf8') => obj ? (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {Object.entries(obj).filter(([, v]) => typeof v !== 'object').map(([k, v]) => (
        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</span>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color }}>{String(v)}</span>
        </div>
      ))}
    </div>
  ) : null;

  return (
    <div className="page-container">
      <SectionHeader title="Software Estimation" subtitle="COCOMO, Function Point Analysis, Cost & Team estimation" icon={<TrendingUp size={20} />}
        action={<GenerateButton projectId={id} module="estimation" label="Generate Estimates" onSuccess={() => { qc.invalidateQueries({ queryKey: ['estimation', id] }); refetch(); }} />} />

      {content && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-default)', paddingBottom: '0.5rem' }}>
          {[['cocomo', 'COCOMO'], ['fp', 'Function Points'], ['cost', 'Cost'], ['team', 'Team']].map(([t, l]) => (
            <button key={t} className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab(t as any)}>{l}</button>
          ))}
        </div>
      )}

      {isLoading ? <CardSkeleton /> : !content ? (
        <EmptyState icon={<TrendingUp size={32} />} title="No estimation generated" description="Generate COCOMO, Function Point Analysis, time, cost, and team size estimations." />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {tab === 'cocomo' && (
            <>
              <div className="card" style={{ padding: '1.25rem' }}><h3 style={{ marginBottom: '1rem', color: '#818cf8', fontWeight: 600 }}>COCOMO Model</h3>{renderKV(content.cocomo, '#818cf8')}</div>
              {content.cocomo?.calculation_steps && (
                <div className="card" style={{ padding: '1.25rem' }}><h3 style={{ marginBottom: '1rem', color: '#818cf8', fontWeight: 600 }}>Calculation Steps</h3>
                  {content.cocomo.calculation_steps.map((s: string, i: number) => <p key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.375rem' }}>{i + 1}. {s}</p>)}
                </div>
              )}
            </>
          )}
          {tab === 'fp' && (
            <>
              <div className="card" style={{ padding: '1.25rem' }}><h3 style={{ marginBottom: '1rem', color: '#38bdf8', fontWeight: 600 }}>Function Point Analysis</h3>{renderKV(content.function_point, '#38bdf8')}</div>
              {content.time_estimation && <div className="card" style={{ padding: '1.25rem' }}><h3 style={{ marginBottom: '1rem', color: '#4ade80', fontWeight: 600 }}>Time Estimation (PERT)</h3>{renderKV(content.time_estimation, '#4ade80')}</div>}
            </>
          )}
          {tab === 'cost' && (
            <div className="card" style={{ padding: '1.25rem', gridColumn: 'span 2' }}><h3 style={{ marginBottom: '1rem', color: '#fbbf24', fontWeight: 600 }}>Cost Estimation</h3>{renderKV(content.cost_estimation, '#fbbf24')}</div>
          )}
          {tab === 'team' && content.team_estimation && (
            <div className="card" style={{ padding: '1.25rem', gridColumn: 'span 2' }}>
              <h3 style={{ marginBottom: '1rem', color: '#c084fc', fontWeight: 600 }}>Team Estimation</h3>
              {renderKV({ recommended_team_size: content.team_estimation.recommended_team_size }, '#c084fc')}
              {content.team_estimation.roles?.length > 0 && (
                <table className="data-table" style={{ marginTop: '1rem' }}><thead><tr><th>Role</th><th>Count</th><th>Responsibilities</th></tr></thead>
                  <tbody>{content.team_estimation.roles.map((r: any, i: number) => (
                    <tr key={i}><td style={{ fontWeight: 600 }}>{r.role}</td><td>{r.count}</td><td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{r.responsibilities}</td></tr>
                  ))}</tbody>
                </table>
              )}
            </div>
          )}
        </div>
      )}

      {content?.summary && (
        <div className="card" style={{ padding: '1.25rem', marginTop: '1rem', borderLeft: '3px solid var(--color-brand-500)', gridColumn: 'span 2' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>EXECUTIVE SUMMARY</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.7 }}>{content.summary}</p>
        </div>
      )}
    </div>
  );
}


// ─── Traceability Page ────────────────────────────────────────────────────────
export function TraceabilityPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();

  const { data, isLoading, refetch } = useQuery({ queryKey: ['traceability', id], queryFn: () => generationService.getTraceability(id) });
  const content = data?.content;
  const matrix = content?.matrix || [];

  return (
    <div className="page-container">
      <SectionHeader title="Traceability Matrix" subtitle="Requirements mapped through design, implementation, and testing" icon={<Link2 size={20} />}
        action={<GenerateButton projectId={id} module="traceability" label="Generate RTM" onSuccess={() => { qc.invalidateQueries({ queryKey: ['traceability', id] }); refetch(); }} />} />

      {matrix.length > 0 && (
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <div className="card" style={{ padding: '1rem', textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#818cf8' }}>{content?.coverage_percentage?.toFixed(1)}%</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Coverage</div>
          </div>
          <div className="card" style={{ padding: '1rem', textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>{content?.summary?.covered || 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Covered</div>
          </div>
          <div className="card" style={{ padding: '1rem', textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fbbf24' }}>{content?.summary?.partially_covered || 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Partial</div>
          </div>
          <div className="card" style={{ padding: '1rem', textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f87171' }}>{content?.summary?.not_covered || 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Not Covered</div>
          </div>
        </div>
      )}

      {isLoading ? <CardSkeleton /> : matrix.length === 0 ? (
        <EmptyState icon={<Link2 size={32} />} title="RTM not generated" description="Generate the Requirement Traceability Matrix linking requirements to design, implementation, and test cases." />
      ) : (
        <div className="card" style={{ padding: '1.25rem', overflowX: 'auto' }}>
          <table className="data-table">
            <thead><tr><th>Req ID</th><th>Requirement</th><th>Design</th><th>Implementation</th><th>Test Cases</th><th>Status</th><th>Coverage</th></tr></thead>
            <tbody>
              {matrix.map((row: any, i: number) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'monospace', color: '#818cf8', fontSize: '0.75rem', fontWeight: 700 }}>{row.requirement_id}</td>
                  <td style={{ maxWidth: 180, fontSize: '0.8rem' }}>{row.requirement_title}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{row.design_component}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{row.implementation_module}</td>
                  <td>{row.test_case_ids?.map((t: string, j: number) => <span key={j} className="badge badge-info" style={{ fontSize: '0.65rem', marginRight: 2 }}>{t}</span>)}</td>
                  <td><span className={`badge ${row.test_status === 'Pass' ? 'badge-success' : row.test_status === 'Fail' ? 'badge-error' : 'badge-neutral'}`} style={{ fontSize: '0.7rem' }}>{row.test_status}</span></td>
                  <td><span className={`badge ${row.coverage_status === 'covered' ? 'badge-success' : row.coverage_status === 'partially_covered' ? 'badge-warning' : 'badge-error'}`} style={{ fontSize: '0.7rem' }}>{row.coverage_status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}


// ─── Quality Metrics Page ─────────────────────────────────────────────────────
import { Radar as RadarChart } from 'react-chartjs-2';

export function MetricsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();

  const { data, isLoading, refetch } = useQuery({ queryKey: ['metrics', id], queryFn: () => generationService.getMetrics(id) });
  const content = data?.content;
  const metrics = content?.metrics || {};
  const chartsData = content?.charts_data || {};

  const radarData = chartsData?.quality_radar ? {
    labels: chartsData.quality_radar.labels,
    datasets: [{ label: 'Quality Score', data: chartsData.quality_radar.values, fill: true, backgroundColor: 'rgba(99,102,241,0.2)', borderColor: '#6366f1', pointBackgroundColor: '#6366f1', pointBorderColor: '#fff', pointHoverBackgroundColor: '#fff', pointHoverBorderColor: '#6366f1' }],
  } : null;

  const METRIC_CONFIGS: Array<{ key: string; label: string; color: string; unit?: string }> = [
    { key: 'cyclomatic_complexity', label: 'Cyclomatic Complexity', color: '#818cf8' },
    { key: 'defect_density', label: 'Defect Density', color: '#f87171', unit: 'defects/KLOC' },
    { key: 'maintainability_index', label: 'Maintainability Index', color: '#4ade80', unit: '/100' },
    { key: 'requirement_coverage', label: 'Requirement Coverage', color: '#38bdf8', unit: '%' },
    { key: 'code_coverage_target', label: 'Code Coverage Target', color: '#fbbf24', unit: '%' },
    { key: 'technical_debt', label: 'Technical Debt', color: '#fb923c', unit: 'hours' },
  ];

  return (
    <div className="page-container">
      <SectionHeader title="Quality Metrics Dashboard" subtitle="Software quality and productivity measurements" icon={<BarChart3 size={20} />}
        action={<GenerateButton projectId={id} module="metrics" label="Generate Metrics" onSuccess={() => { qc.invalidateQueries({ queryKey: ['metrics', id] }); refetch(); }} />} />

      {isLoading ? <CardSkeleton /> : !metrics || Object.keys(metrics).length === 0 ? (
        <EmptyState icon={<BarChart3 size={32} />} title="Quality metrics not generated" description="Generate quality metrics dashboard with cyclomatic complexity, defect density, coverage, and productivity charts." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Radar Chart */}
          {radarData && (
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Quality Radar</h3>
              <div style={{ height: 280 }}><RadarChart data={radarData} options={{ ...CHART_OPTIONS, scales: { r: CHART_OPTIONS.scales.r } }} /></div>
            </div>
          )}

          {/* Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {METRIC_CONFIGS.map(({ key, label, color }) => {
              const m = metrics[key];
              if (!m) return null;
              const val = m.value ?? m.average ?? m.covered_percentage ?? m.target_percentage ?? m.estimated_hours;
              const status = m.status || (m.velocity_trend ? m.velocity_trend : null);
              const STATUS_STYLES: Record<string, string> = { good: 'badge-success', warning: 'badge-warning', critical: 'badge-error', stable: 'badge-success', unstable: 'badge-error', increasing: 'badge-success', stable2: 'badge-neutral', decreasing: 'badge-error' };
              return (
                <div key={key} className="card" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</span>
                    {status && <span className={`badge ${STATUS_STYLES[status] || 'badge-neutral'}`} style={{ fontSize: '0.68rem' }}>{status.replace('2', '')}</span>}
                  </div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, color, letterSpacing: '-0.03em' }}>{val?.toFixed ? val.toFixed(1) : val}</div>
                  {m.description && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem', lineHeight: 1.5 }}>{m.description}</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}


// ─── Maintenance Plan Page ────────────────────────────────────────────────────
export function MaintenancePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId || '0');
  const qc = useQueryClient();

  const { data, isLoading, refetch } = useQuery({ queryKey: ['maintenance', id], queryFn: () => generationService.getMaintenance(id) });
  const content = data?.content;

  const TYPES = [
    { key: 'corrective_maintenance', title: 'Corrective', color: '#f87171', desc: 'Bug fixes and defect corrections' },
    { key: 'adaptive_maintenance', title: 'Adaptive', color: '#38bdf8', desc: 'Adaptation to environment changes' },
    { key: 'preventive_maintenance', title: 'Preventive', color: '#4ade80', desc: 'Proactive quality improvements' },
    { key: 'perfective_maintenance', title: 'Perfective', color: '#fbbf24', desc: 'Enhancements and new features' },
  ];

  return (
    <div className="page-container">
      <SectionHeader title="Maintenance Plan" subtitle="Post-deployment maintenance strategy and schedule" icon={<Wrench size={20} />}
        action={<GenerateButton projectId={id} module="maintenance" label="Generate Maintenance Plan" onSuccess={() => { qc.invalidateQueries({ queryKey: ['maintenance', id] }); refetch(); }} />} />

      {isLoading ? <CardSkeleton /> : !content ? (
        <EmptyState icon={<Wrench size={32} />} title="Maintenance plan not generated" description="Generate a comprehensive software maintenance plan covering corrective, adaptive, preventive, and perfective maintenance." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Overview */}
          {content.overview && (
            <div className="card" style={{ padding: '1.25rem', borderLeft: '3px solid var(--color-brand-500)' }}>
              <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Overview</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{content.overview.maintenance_approach}</p>
            </div>
          )}

          {/* Maintenance types grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem' }}>
            {TYPES.map(({ key, title, color, desc }) => {
              const section = content[key];
              if (!section) return null;
              return (
                <div key={key} className="card" style={{ padding: '1.25rem', borderTop: `3px solid ${color}` }}>
                  <div style={{ fontWeight: 700, color, fontSize: '0.95rem', marginBottom: '0.25rem' }}>{title} Maintenance</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{desc}</div>
                  {section.description && <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.75rem' }}>{section.description}</p>}
                  {section.process?.length > 0 && (
                    <div>
                      {section.process.slice(0, 4).map((step: string, i: number) => (
                        <div key={i} style={{ display: 'flex', gap: '0.375rem', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                          <span style={{ color, fontWeight: 700, flexShrink: 0 }}>{i + 1}.</span> {step}
                        </div>
                      ))}
                    </div>
                  )}
                  {section.sla && (
                    <div style={{ marginTop: '0.75rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.375rem' }}>
                      {Object.entries(section.sla).map(([k, v]) => (
                        <div key={k} style={{ background: 'var(--bg-overlay)', padding: '0.375rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.7rem' }}>
                          <div style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</div>
                          <div style={{ fontWeight: 600, color }}>{String(v)}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Metrics */}
          {content.maintenance_metrics && (
            <div className="card" style={{ padding: '1.25rem' }}>
              <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Maintenance KPIs</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.75rem' }}>
                {Object.entries(content.maintenance_metrics).map(([k, v]) => (
                  <div key={k} style={{ background: 'var(--bg-overlay)', padding: '0.875rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a78bfa', marginBottom: '0.25rem' }}>{String(v)}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
