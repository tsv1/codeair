import { useState } from 'react';
import { useAuth } from './AuthContext';
import { logout as logoutApi } from './api';

export function Dashboard() {
  const { user, token, logout } = useAuth();
  const [dropdownActive, setDropdownActive] = useState(false);

  if (!user) {
    return null;
  }

  const handleLogout = async () => {
    if (token) {
      try {
        await logoutApi(token);
      } catch (error) {
        console.error('Logout API call failed:', error);
      }
    }
    logout();
  };

  return (
    <>
      <nav className="navbar" role="navigation" aria-label="main navigation">
        <div className="container">
          <div className="navbar-brand">
            <span className="navbar-item">
              <strong>CodeAir</strong>
            </span>
          </div>

          <div className="navbar-menu">
            <div className="navbar-end">
              <div className={`navbar-item has-dropdown ${dropdownActive ? 'is-active' : ''}`}>
                <a
                  className="navbar-link"
                  onClick={(e) => { e.preventDefault(); setDropdownActive(!dropdownActive); }}
                >
                  {user.username}
                </a>
                <div className="navbar-dropdown is-right">
                  <a
                    className="navbar-item"
                    onClick={(e) => { e.preventDefault(); handleLogout(); }}
                  >
                    Logout
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 className="title">Welcome, {user.name}!</h1>
            <p className="subtitle">You are successfully logged in.</p>
          </div>
        </div>
      </section>
    </>
  );
}
