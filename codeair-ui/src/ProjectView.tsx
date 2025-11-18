import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { logout as logoutApi, getProject, type Project } from './api';
import { ExternalLink, ArrowLeft } from 'lucide-react';

interface ProjectViewProps {
  projectId: number;
}

export function ProjectView({ projectId }: ProjectViewProps) {
  const { user, token, logout } = useAuth();
  const [dropdownActive, setDropdownActive] = useState(false);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    setIsLoading(true);
    setError(null);

    getProject(projectId, token)
      .then((response) => {
        setProject(response.project);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load project');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [projectId, token]);

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

  const handleBack = () => {
    window.location.href = '/';
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
          <div className="box" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <button className="button is-text mb-4" onClick={handleBack}>
              <span className="icon">
                <ArrowLeft size={16} />
              </span>
              <span>Back to Search</span>
            </button>

            {isLoading && (
              <div className="has-text-centered py-6">
                <p>Loading project...</p>
              </div>
            )}

            {error && (
              <div className="notification is-danger is-light">
                {error}
              </div>
            )}

            {project && !isLoading && (
              <div>
                <article className="media">
                  <figure className="media-left">
                    <p className="image is-128x128">
                      {project.avatar_url ? (
                        <img src={project.avatar_url} alt={project.name} />
                      ) : (
                        <div
                          style={{
                            width: '128px',
                            height: '128px',
                            backgroundColor: '#f5f5f5',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderRadius: '4px',
                          }}
                        >
                          <span style={{ fontSize: '48px', color: '#999' }}>
                            {project.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                    </p>
                  </figure>
                  <div className="media-content">
                    <div className="content">
                      <h1 className="title is-3 mb-2">{project.name_with_namespace}</h1>
                      {project.description && (
                        <p className="subtitle is-6 has-text-grey mb-3">
                          {project.description}
                        </p>
                      )}
                      <a
                        href={project.web_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="button is-link is-light"
                      >
                        <span>View on GitLab</span>
                        <span className="icon">
                          <ExternalLink size={16} />
                        </span>
                      </a>
                    </div>
                  </div>
                </article>
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
