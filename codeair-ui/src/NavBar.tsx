import { useState } from 'react';
import { useAuth } from './AuthContext';
import { logout as logoutApi } from './api';

export function Navbar() {
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
    <nav className="navbar" role="navigation" aria-label="main navigation">
      <div className="container">
        <div className="navbar-brand">
          <a
            href="/"
            className="navbar-item"
            onClick={(e) => {
              e.preventDefault();
              window.location.href = '/';
            }}
          >
            <strong>CodeAir</strong>
          </a>
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
  );
}
