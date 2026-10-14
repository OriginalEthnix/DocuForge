import React from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Zap, Mail, Lock, User, Building2, ArrowRight, Loader2, Eye, EyeOff, AlertCircle, UserPlus, Info } from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';
import { getErrorMessage } from '@/services/api';

// ─── Login Page ───────────────────────────────────────────────────────────────

const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, 'Email address is required')
    .email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [apiError, setApiError] = React.useState('');
  const [showPass, setShowPass] = React.useState(false);
  const [showForgotNotice, setShowForgotNotice] = React.useState(false);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setApiError('');
    setShowForgotNotice(false);
    try {
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (err: any) {
      const status = err?.response?.status;
      const detailMsg = typeof err?.response?.data?.detail === 'string'
        ? err.response.data.detail.toLowerCase()
        : '';
      const isUserNotFound =
        status === 404 ||
        err?.response?.data?.code === 'USER_NOT_FOUND' ||
        detailMsg.includes('no account found') ||
        detailMsg.includes('user not found');

      if (isUserNotFound) {
        navigate('/register', {
          state: {
            email: data.email.trim(),
            message: 'No account found with this email. Create an account to get started.',
          },
        });
        return;
      }

      setApiError(getErrorMessage(err));
    }
  };

  return (
    <AuthLayout>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        style={{ width: '100%', maxWidth: 420 }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            style={{
              width: 56,
              height: 56,
              borderRadius: 'var(--radius-lg)',
              background: 'var(--gradient-brand)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.25rem',
              boxShadow: 'var(--shadow-brand)',
            }}
          >
            <Zap size={28} color="white" />
          </motion.div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '0.375rem' }}>
            Welcome back
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Sign in to DocuForge AI
          </p>
        </div>

        {/* Form */}
        <div className="card" style={{ padding: 'clamp(1.25rem, 4vw, 2rem)' }}>
          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {apiError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                style={{
                  padding: '0.75rem 1rem',
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  borderRadius: 'var(--radius-md)',
                  color: '#f87171',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{apiError}</span>
              </motion.div>
            )}

            <FormField label="Email address" error={errors.email?.message}>
              <InputWithIcon icon={<Mail size={16} />}>
                <input
                  type="email"
                  placeholder="you@example.com"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem' }}
                  disabled={isSubmitting}
                  {...register('email')}
                />
              </InputWithIcon>
            </FormField>

            <FormField label="Password" error={errors.password?.message}>
              <InputWithIcon
                icon={<Lock size={16} />}
                rightIcon={
                  <button type="button" onClick={() => setShowPass(!showPass)} style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
                    {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                }
              >
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="••••••••"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                  disabled={isSubmitting}
                  {...register('password')}
                />
              </InputWithIcon>
            </FormField>

            {/* Forgot password option */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '-0.25rem' }}>
              <button
                type="button"
                onClick={() => setShowForgotNotice((prev) => !prev)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-brand-400)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  padding: 0,
                  fontWeight: 500,
                }}
              >
                Forgot password?
              </button>
            </div>

            {showForgotNotice && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  padding: '0.625rem 0.875rem',
                  background: 'rgba(99, 102, 241, 0.08)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.8rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                }}
              >
                <Info size={15} style={{ color: 'var(--color-brand-400)', flexShrink: 0, marginTop: '0.125rem' }} />
                <span>
                  Password reset is managed by your workspace administrator or support team at support@docuforge.ai.
                </span>
              </motion.div>
            )}

            <motion.button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '0.5rem' }}
              disabled={isSubmitting}
              whileHover={!isSubmitting ? { scale: 1.01 } : {}}
              whileTap={!isSubmitting ? { scale: 0.99 } : {}}
            >
              {isSubmitting ? <Loader2 size={18} style={{ animation: 'spin-slow 0.6s linear infinite' }} /> : null}
              {isSubmitting ? 'Signing in...' : 'Sign in'}
              {!isSubmitting && <ArrowRight size={16} />}
            </motion.button>
          </form>
        </div>

        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '1.5rem' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--color-brand-400)', fontWeight: 600, textDecoration: 'none' }}>
            Create one
          </Link>
        </p>
      </motion.div>
    </AuthLayout>
  );
}

// ─── Register Page ────────────────────────────────────────────────────────────

const registerSchema = z.object({
  full_name: z.string().trim().min(2, 'Full name must be at least 2 characters'),
  email: z
    .string()
    .trim()
    .min(1, 'Email address is required')
    .email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  organization: z.string().trim().optional(),
});

type RegisterForm = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { register: registerUser } = useAuthStore();
  const [apiError, setApiError] = React.useState('');
  const [showPass, setShowPass] = React.useState(false);

  // Extract prefilled email and friendly message from navigation state or URL query parameter
  const stateData = location.state as { email?: string; message?: string } | null;
  const searchParams = new URLSearchParams(location.search);
  const initialEmail = stateData?.email || searchParams.get('email') || '';
  const initialNotice = stateData?.message || (initialEmail ? 'No account found with this email. Create an account to get started.' : '');

  const [notice, setNotice] = React.useState(initialNotice);

  const { register, handleSubmit, formState: { errors, isSubmitting }, setValue } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: initialEmail,
      full_name: '',
      password: '',
      organization: '',
    },
  });

  React.useEffect(() => {
    if (initialEmail) {
      setValue('email', initialEmail, { shouldValidate: true });
    }
  }, [initialEmail, setValue]);

  const onSubmit = async (data: RegisterForm) => {
    setApiError('');
    setNotice('');
    try {
      await registerUser(data);
      navigate('/dashboard');
    } catch (err) {
      setApiError(getErrorMessage(err));
    }
  };

  return (
    <AuthLayout>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ width: '100%', maxWidth: 440 }}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            style={{
              width: 56, height: 56,
              borderRadius: 'var(--radius-lg)',
              background: 'var(--gradient-brand)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1.25rem',
              boxShadow: 'var(--shadow-brand)',
            }}
          >
            <Zap size={28} color="white" />
          </motion.div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '0.375rem' }}>
            Create account
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Start generating professional SE documentation
          </p>
        </div>

        <div className="card" style={{ padding: 'clamp(1.25rem, 4vw, 2rem)' }}>
          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {notice && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  padding: '0.75rem 1rem',
                  background: 'rgba(99, 102, 241, 0.12)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--color-brand-300)',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <UserPlus size={16} style={{ flexShrink: 0, color: 'var(--color-brand-400)' }} />
                <span>{notice}</span>
              </motion.div>
            )}

            {apiError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                style={{
                  padding: '0.75rem 1rem',
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  borderRadius: 'var(--radius-md)',
                  color: '#f87171',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{apiError}</span>
              </motion.div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 160px), 1fr))', gap: '1rem' }}>
              <FormField label="Full Name" error={errors.full_name?.message}>
                <InputWithIcon icon={<User size={16} />}>
                  <input
                    type="text"
                    placeholder="John Doe"
                    className="input-field"
                    style={{ paddingLeft: '2.5rem' }}
                    disabled={isSubmitting}
                    {...register('full_name')}
                  />
                </InputWithIcon>
              </FormField>
              <FormField label="Organization" error={errors.organization?.message}>
                <InputWithIcon icon={<Building2 size={16} />}>
                  <input
                    type="text"
                    placeholder="Optional"
                    className="input-field"
                    style={{ paddingLeft: '2.5rem' }}
                    disabled={isSubmitting}
                    {...register('organization')}
                  />
                </InputWithIcon>
              </FormField>
            </div>

            <FormField label="Email address" error={errors.email?.message}>
              <InputWithIcon icon={<Mail size={16} />}>
                <input
                  type="email"
                  placeholder="you@example.com"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem' }}
                  disabled={isSubmitting}
                  {...register('email')}
                />
              </InputWithIcon>
            </FormField>

            <FormField label="Password" error={errors.password?.message}>
              <InputWithIcon icon={<Lock size={16} />} rightIcon={
                <button type="button" onClick={() => setShowPass(!showPass)} style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              }>
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="At least 8 characters"
                  className="input-field"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                  disabled={isSubmitting}
                  {...register('password')}
                />
              </InputWithIcon>
            </FormField>

            <motion.button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '0.5rem' }}
              disabled={isSubmitting}
              whileHover={!isSubmitting ? { scale: 1.01 } : {}}
              whileTap={!isSubmitting ? { scale: 0.99 } : {}}
            >
              {isSubmitting ? <Loader2 size={18} style={{ animation: 'spin-slow 0.6s linear infinite' }} /> : null}
              {isSubmitting ? 'Creating account...' : 'Create Account'}
              {!isSubmitting && <ArrowRight size={16} />}
            </motion.button>
          </form>
        </div>

        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '1.5rem' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--color-brand-400)', fontWeight: 600, textDecoration: 'none' }}>
            Sign in
          </Link>
        </p>
      </motion.div>
    </AuthLayout>
  );
}

// ─── Shared Auth Layout ───────────────────────────────────────────────────────

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'clamp(1rem, 4vw, 2rem)',
      background: 'var(--bg-base)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Decorative gradient orbs */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        left: '-5%',
        width: 600,
        height: 600,
        background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-10%',
        right: '-5%',
        width: 500,
        height: 500,
        background: 'radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{ position: 'relative', zIndex: 1, width: '100%', display: 'flex', justifyContent: 'center' }}>
        {children}
      </div>
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function FormField({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
      <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</label>
      {children}
      {error && <span style={{ fontSize: '0.75rem', color: '#f87171' }}>{error}</span>}
    </div>
  );
}

function InputWithIcon({
  icon,
  rightIcon,
  children,
}: {
  icon: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div style={{ position: 'relative' }}>
      <div style={{
        position: 'absolute',
        left: '0.75rem',
        top: '50%',
        transform: 'translateY(-50%)',
        color: 'var(--text-muted)',
        pointerEvents: 'none',
        zIndex: 1,
      }}>
        {icon}
      </div>
      {children}
      {rightIcon && (
        <div style={{
          position: 'absolute',
          right: '0.75rem',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1,
        }}>
          {rightIcon}
        </div>
      )}
    </div>
  );
}
