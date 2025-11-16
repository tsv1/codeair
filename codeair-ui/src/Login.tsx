import { useState } from 'react';
import { Gitlab } from 'lucide-react';
import { getLoginUrl } from './api';

export function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const { authorization_url } = await getLoginUrl();
      window.location.href = authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate login');
      setLoading(false);
    }
  };

  return (
    <section className="section">
      <div className="container">
        <div className="box" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h1 className="title">Welcome to CodeAir</h1>
          <p className="subtitle">Please sign in with your GitLab account to continue.</p>

          {error && (
            <div className="notification is-danger is-light">
              {error}
            </div>
          )}

          <button
            onClick={handleLogin}
            disabled={loading}
            className={`button is-fullwidth ${loading ? 'is-loading' : ''}`}
            style={{
              backgroundColor: '#FC6D26',
              borderColor: '#FC6D26',
              color: 'white',
            }}
            onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#E85615')}
            onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = '#FC6D26')}
          >
            <span className="icon">
              <Gitlab size={20} />
            </span>
            <span>Sign in with GitLab</span>
          </button>
        </div>
      </div>
    </section>
  );
}
