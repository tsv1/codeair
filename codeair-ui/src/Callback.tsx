import { useEffect, useState, useRef } from 'react';
import { useAuth } from './AuthContext';
import { handleCallback } from './api';

export function Callback() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) {
      return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (!code) {
      setError('No authorization code found');
      return;
    }

    hasProcessed.current = true;

    handleCallback(code)
      .then(({ token, user }) => {
        login(token, user);
        window.location.href = '/';
      })
      .catch((err) => {
        hasProcessed.current = false;
        setError(err instanceof Error ? err.message : 'Authentication failed');
      });
  }, [login]);

  if (error) {
    return (
      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 className="title">Authentication Error</h1>
            <div className="notification is-danger is-light">
              {error}
            </div>
            <a href="/" className="button is-primary">Go back to login</a>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="section">
      <div className="container">
        <div className="box" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h1 className="title">Authenticating...</h1>
          <p>Please wait while we complete your sign in.</p>
        </div>
      </div>
    </section>
  );
}
