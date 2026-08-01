import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ChevronRight, ChevronLeft, Plus, X, Check, Loader2,
  FileText, Code2, Users, Calendar, Target, Rocket,
} from 'lucide-react';
import { projectService } from '@/services/project.service';
import { ProjectCreate } from '@/types';
import { getErrorMessage } from '@/services/api';

const DOMAINS = [
  { value: 'web', label: 'Web App', emoji: '🌐' },
  { value: 'mobile', label: 'Mobile', emoji: '📱' },
  { value: 'desktop', label: 'Desktop', emoji: '💻' },
  { value: 'ai_ml', label: 'AI / ML', emoji: '🤖' },
  { value: 'fintech', label: 'FinTech', emoji: '💰' },
  { value: 'healthcare', label: 'Healthcare', emoji: '🏥' },
  { value: 'ecommerce', label: 'E-Commerce', emoji: '🛒' },
  { value: 'education', label: 'Education', emoji: '📚' },
  { value: 'embedded', label: 'Embedded', emoji: '⚙️' },
  { value: 'other', label: 'Other', emoji: '🔧' },
];

const TECH_SUGGESTIONS = [
  'React', 'Vue.js', 'Angular', 'Next.js', 'Svelte',
  'FastAPI', 'Django', 'Express.js', 'Spring Boot', 'Laravel',
  'PostgreSQL', 'MySQL', 'MongoDB', 'SQLite', 'Redis',
  'Docker', 'Kubernetes', 'AWS', 'Firebase', 'GraphQL',
  'TypeScript', 'Python', 'Java', 'Go', 'Rust',
];

const schema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(255),
  description: z.string().min(20, 'Description must be at least 20 characters'),
  problem_statement: z.string().optional(),
  objectives: z.string().optional(),
  domain: z.string().min(1, 'Please select a domain'),
  target_users: z.string().optional(),
  team_size: z.coerce.number().min(1).max(1000),
  timeline_weeks: z.coerce.number().min(1).max(520),
});

type FormData = z.infer<typeof schema>;

const STEPS = [
  { title: 'Project Basics', icon: FileText, description: 'Name and describe your project' },
  { title: 'Domain & Users', icon: Target, description: 'Define scope and target audience' },
  { title: 'Tech & Team', icon: Code2, description: 'Technology stack and team details' },
  { title: 'Deliverables', icon: Rocket, description: 'Stakeholders and expected outputs' },
];

export function CreateProjectPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [step, setStep] = React.useState(0);
  const [techStack, setTechStack] = React.useState<string[]>([]);
  const [stakeholders, setStakeholders] = React.useState<string[]>([]);
  const [deliverables, setDeliverables] = React.useState<string[]>([]);
  const [techInput, setTechInput] = React.useState('');
  const [stakeInput, setStakeInput] = React.useState('');
  const [delivInput, setDelivInput] = React.useState('');
  const [apiError, setApiError] = React.useState('');

  const { register, handleSubmit, formState: { errors }, watch, trigger } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { domain: 'web', team_size: 4, timeline_weeks: 12 },
  });

  const mutation = useMutation({
    mutationFn: projectService.create,
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      navigate(`/projects/${project.id}`);
    },
    onError: (err) => setApiError(getErrorMessage(err)),
  });

  const watchDomain = watch('domain');

  const nextStep = async () => {
    const fieldsToValidate: (keyof FormData)[][] = [
      ['title', 'description'],
      ['domain', 'target_users', 'problem_statement', 'objectives'],
      ['team_size', 'timeline_weeks'],
      [],
    ];
    const valid = await trigger(fieldsToValidate[step] as any);
    if (valid) setStep(s => Math.min(s + 1, STEPS.length - 1));
  };

  const onSubmit = (data: FormData) => {
    setApiError('');
    const payload: ProjectCreate = {
      ...data,
      tech_stack: techStack,
      stakeholders,
      expected_deliverables: deliverables,
    };
    mutation.mutate(payload);
  };

  const addTag = (value: string, setter: React.Dispatch<React.SetStateAction<string[]>>, inputSetter: React.Dispatch<React.SetStateAction<string>>) => {
    if (value.trim()) {
      setter(prev => [...prev, value.trim()]);
      inputSetter('');
    }
  };
  const removeTag = (index: number, setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="page-container" style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: '2rem' }}>
        <button className="btn btn-ghost btn-sm" style={{ marginBottom: '1rem' }} onClick={() => navigate('/projects')}>
          <ChevronLeft size={16} /> Back to Projects
        </button>
        <h1 style={{ fontSize: '1.625rem', fontWeight: 700, letterSpacing: '-0.02em' }}>Create New Project</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 2 }}>
          Fill in your project details and DocuForge AI will generate comprehensive documentation.
        </p>
      </motion.div>

      {/* Step Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}
      >
        {STEPS.map((s, i) => (
          <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{
              height: 3,
              borderRadius: 'var(--radius-full)',
              background: i <= step ? 'var(--gradient-brand)' : 'var(--bg-hover)',
              transition: 'background 0.3s ease',
            }} />
            <div style={{ fontSize: '0.7rem', color: i === step ? 'var(--color-brand-400)' : 'var(--text-muted)', fontWeight: i === step ? 600 : 400 }}>
              Step {i + 1}: {s.title}
            </div>
          </div>
        ))}
      </motion.div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.25 }}
          >
            {/* Step 0: Basics */}
            {step === 0 && (
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Project Basics</h2>

                <FormGroup label="Project Title *" error={errors.title?.message}>
                  <input className="input-field" placeholder="e.g. Student Management System" {...register('title')} />
                </FormGroup>

                <FormGroup label="Project Description *" error={errors.description?.message}>
                  <textarea
                    className="input-field"
                    rows={4}
                    placeholder="Describe what your software does, its main purpose, and key features..."
                    style={{ resize: 'vertical' }}
                    {...register('description')}
                  />
                </FormGroup>

                <FormGroup label="Problem Statement" error={errors.problem_statement?.message}>
                  <textarea
                    className="input-field"
                    rows={3}
                    placeholder="What problem does this software solve?"
                    style={{ resize: 'vertical' }}
                    {...register('problem_statement')}
                  />
                </FormGroup>

                <FormGroup label="Project Objectives" error={errors.objectives?.message}>
                  <textarea
                    className="input-field"
                    rows={3}
                    placeholder="List the main objectives of this project..."
                    style={{ resize: 'vertical' }}
                    {...register('objectives')}
                  />
                </FormGroup>
              </div>
            )}

            {/* Step 1: Domain & Users */}
            {step === 1 && (
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Domain & Target Users</h2>

                <FormGroup label="Project Domain *" error={errors.domain?.message}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem' }}>
                    {DOMAINS.map(d => (
                      <label
                        key={d.value}
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          padding: '0.75rem 0.5rem',
                          borderRadius: 'var(--radius-md)',
                          border: `1px solid ${watchDomain === d.value ? 'var(--color-brand-500)' : 'var(--border-default)'}`,
                          background: watchDomain === d.value ? 'rgba(99,102,241,0.1)' : 'var(--bg-elevated)',
                          cursor: 'pointer',
                          transition: 'all var(--transition-fast)',
                          gap: '0.3rem',
                          fontSize: '0.75rem',
                          fontWeight: watchDomain === d.value ? 600 : 400,
                          color: watchDomain === d.value ? 'var(--color-brand-400)' : 'var(--text-secondary)',
                          textAlign: 'center',
                        }}
                      >
                        <input type="radio" style={{ display: 'none' }} value={d.value} {...register('domain')} />
                        <span style={{ fontSize: '1.5rem' }}>{d.emoji}</span>
                        {d.label}
                      </label>
                    ))}
                  </div>
                </FormGroup>

                <FormGroup label="Target Users" error={errors.target_users?.message}>
                  <textarea
                    className="input-field"
                    rows={3}
                    placeholder="Who will use this software? (e.g. University students, Healthcare providers, Small business owners)"
                    style={{ resize: 'vertical' }}
                    {...register('target_users')}
                  />
                </FormGroup>
              </div>
            )}

            {/* Step 2: Tech & Team */}
            {step === 2 && (
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Technology & Team</h2>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <FormGroup label="Team Size *" error={errors.team_size?.message}>
                    <input type="number" className="input-field" min={1} max={1000} {...register('team_size')} />
                  </FormGroup>
                  <FormGroup label="Timeline (weeks) *" error={errors.timeline_weeks?.message}>
                    <input type="number" className="input-field" min={1} max={520} {...register('timeline_weeks')} />
                  </FormGroup>
                </div>

                <FormGroup label="Technology Stack">
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.625rem', flexWrap: 'wrap' }}>
                    {techStack.map((tech, i) => (
                      <span key={i} className="badge badge-brand" style={{ gap: '0.4rem' }}>
                        {tech}
                        <button type="button" onClick={() => removeTag(i, setTechStack)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0, lineHeight: 1 }}>
                          <X size={11} />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      className="input-field"
                      placeholder="Add technology..."
                      value={techInput}
                      onChange={e => setTechInput(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(techInput, setTechStack, setTechInput); } }}
                    />
                    <button type="button" className="btn btn-secondary btn-icon" onClick={() => addTag(techInput, setTechStack, setTechInput)}>
                      <Plus size={16} />
                    </button>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginTop: '0.625rem' }}>
                    {TECH_SUGGESTIONS.filter(t => !techStack.includes(t)).slice(0, 10).map(t => (
                      <button
                        key={t}
                        type="button"
                        className="badge badge-neutral"
                        style={{ cursor: 'pointer' }}
                        onClick={() => setTechStack(prev => [...prev, t])}
                      >
                        + {t}
                      </button>
                    ))}
                  </div>
                </FormGroup>
              </div>
            )}

            {/* Step 3: Deliverables */}
            {step === 3 && (
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Stakeholders & Deliverables</h2>

                <FormGroup label="Key Stakeholders">
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.625rem', flexWrap: 'wrap' }}>
                    {stakeholders.map((s, i) => (
                      <span key={i} className="badge badge-purple" style={{ gap: '0.4rem' }}>
                        {s}
                        <button type="button" onClick={() => removeTag(i, setStakeholders)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}>
                          <X size={11} />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input className="input-field" placeholder="e.g. Project Manager, End Users, Developers..." value={stakeInput} onChange={e => setStakeInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(stakeInput, setStakeholders, setStakeInput); } }} />
                    <button type="button" className="btn btn-secondary btn-icon" onClick={() => addTag(stakeInput, setStakeholders, setStakeInput)}><Plus size={16} /></button>
                  </div>
                </FormGroup>

                <FormGroup label="Expected Deliverables">
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.625rem', flexWrap: 'wrap' }}>
                    {deliverables.map((d, i) => (
                      <span key={i} className="badge badge-success" style={{ gap: '0.4rem' }}>
                        {d}
                        <button type="button" onClick={() => removeTag(i, setDeliverables)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}>
                          <X size={11} />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input className="input-field" placeholder="e.g. Web Application, API Documentation, Source Code..." value={delivInput} onChange={e => setDelivInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(delivInput, setDeliverables, setDelivInput); } }} />
                    <button type="button" className="btn btn-secondary btn-icon" onClick={() => addTag(delivInput, setDeliverables, setDelivInput)}><Plus size={16} /></button>
                  </div>
                </FormGroup>

                {apiError && (
                  <div style={{ padding: '0.75rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', color: '#f87171', fontSize: '0.875rem' }}>
                    {apiError}
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem', gap: '1rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setStep(s => s - 1)}
            disabled={step === 0}
          >
            <ChevronLeft size={16} /> Previous
          </button>

          {step < STEPS.length - 1 ? (
            <button type="button" className="btn btn-primary" onClick={nextStep}>
              Continue <ChevronRight size={16} />
            </button>
          ) : (
            <motion.button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={mutation.isPending}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {mutation.isPending ? (
                <><Loader2 size={16} style={{ animation: 'spin-slow 0.6s linear infinite' }} /> Creating Project...</>
              ) : (
                <><Rocket size={16} /> Create Project</>
              )}
            </motion.button>
          )}
        </div>
      </form>
    </div>
  );
}

function FormGroup({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
      <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</label>
      {children}
      {error && <span style={{ fontSize: '0.75rem', color: '#f87171' }}>{error}</span>}
    </div>
  );
}
