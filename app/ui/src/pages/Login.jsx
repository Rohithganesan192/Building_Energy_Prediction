import React, { useState } from 'react';
import { useAuth } from '../store/AuthContext';
import { Button } from '../components/ui/Button';
import { Lock, ArrowRight, ShieldAlert } from 'lucide-react';

export const Login = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(false);
    const success = await login(username, password);
    if (!success) {
      setError(true);
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--surface-secondary)', padding: '1rem' }}>
      <div style={{ width: '100%', maxWidth: 420, background: 'var(--surface-primary)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-medium)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
        
        <div style={{ padding: '2rem 2rem 1.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ width: 40, height: 40, background: 'var(--accent-primary)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Lock size={20} style={{ color: 'white' }} />
            </div>
            <div>
              <h1 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>BEI Platform</h1>
              <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)' }}>Admin / Demo Login</span>
            </div>
          </div>
          <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Welcome to the Explainable Machine Learning for Building Energy Consumption Prediction platform.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '2rem' }}>
          {error && (
            <div style={{ padding: '0.75rem', background: 'rgba(220, 38, 38, 0.1)', color: 'var(--accent-danger)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: 'var(--fs-sm)' }}>
              <ShieldAlert size={16} /> Invalid credentials.
            </div>
          )}
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Username</label>
              <input 
                type="text" 
                className="input" 
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Password</label>
              <input 
                type="password" 
                className="input" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <Button variant="primary" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
            {loading ? 'Authenticating...' : 'Sign In'} <ArrowRight size={16} />
          </Button>
          
          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: 'var(--fs-2xs)', color: 'var(--text-muted)' }}>
            Research configuration. Secure access only.
          </div>
        </form>

      </div>
    </div>
  );
};
