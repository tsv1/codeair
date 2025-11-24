import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getProject, getAgents, getAgentPlaceholders, type Project, type Agent } from './api';
import { ExternalLink, ArrowLeft, Settings } from 'lucide-react';
import { Navbar } from './NavBar';
import { Link } from './Link';

interface ProjectViewProps {
  projectId: number;
}

export function ProjectView({ projectId }: ProjectViewProps) {
  const { user, token } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [error, setError] = useState<string | null>(null);

  if (!user) {
    return null;
  }

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

  useEffect(() => {
    if (!token) return;

    setIsLoadingAgents(true);

    Promise.all([
      getAgents(projectId, token),
      getAgentPlaceholders(projectId, token)
    ])
      .then(([agentsResponse, placeholdersResponse]) => {
        // Get existing agent types
        const existingTypes = new Set(agentsResponse.agents.map(agent => agent.type));

        // Add placeholders only if that agent type doesn't exist
        const placeholdersToAdd = placeholdersResponse.agents.filter(
          placeholder => !existingTypes.has(placeholder.type)
        );

        // Merge actual agents with missing placeholders
        const mergedAgents = [...agentsResponse.agents, ...placeholdersToAdd];
        setAgents(mergedAgents);
      })
      .catch((err) => {
        console.error('Failed to load agents:', err);
        setAgents([]);
      })
      .finally(() => {
        setIsLoadingAgents(false);
      });
  }, [projectId, token]);

  return (
    <>
      <Navbar />

      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <Link href="/" className="button is-text mb-4">
              <span className="icon">
                <ArrowLeft size={16} />
              </span>
              <span>Back to Search</span>
            </Link>

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
                    <div className="image is-128x128">
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
                    </div>
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
                        className="button is-info is-light"
                      >
                        <span>View on GitLab</span>
                        <span className="icon">
                          <ExternalLink size={16} />
                        </span>
                      </a>
                    </div>
                  </div>
                </article>

                <hr />

                <div className="mt-5">
                  <h2 className="title is-4 mb-4">AI Agents</h2>

                  {isLoadingAgents ? (
                    <div className="has-text-centered py-4">
                      <p>Loading agents...</p>
                    </div>
                  ) : agents.length === 0 ? (
                    <div className="notification is-info is-light">
                      No agents configured for this project.
                    </div>
                  ) : (
                    <div>
                      {agents.map((agent) => {
                        // Check if this is a placeholder agent (UUID starts with all zeros)
                        const isPlaceholder = agent.id.startsWith('00000000-0000-0000-0000');
                        const configUrl = isPlaceholder
                          ? `/project/${projectId}/agents/new?type=${agent.type}`
                          : `/project/${projectId}/agents/${agent.id}`;

                        return (
                          <div key={agent.id} className="box mb-3">
                            <div className="is-flex is-justify-content-space-between is-align-items-start">
                              <div style={{ flex: 1 }}>
                                <div className="is-flex is-align-items-center mb-2">
                                  <h3 className="title is-5 mb-0 mr-3">{agent.name}</h3>
                                  <span className={`tag ${agent.enabled ? 'is-success' : 'is-light'}`}>
                                    {agent.enabled ? 'Enabled' : 'Disabled'}
                                  </span>
                                </div>
                                <p className="has-text-grey">{agent.description}</p>
                              </div>
                              <Link
                                href={configUrl}
                                className="button is-link is-light ml-4"
                              >
                                <span className="icon">
                                  <Settings size={16} />
                                </span>
                                <span>Configure</span>
                              </Link>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
