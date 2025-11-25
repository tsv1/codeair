import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getAgent, getAgentPlaceholders, createAgent, updateAgent, getProject, type Agent, type AgentEngine, type AgentType, type Project } from './api';
import { Save, Home, Folder, Bot } from 'lucide-react';
import { Navbar } from './NavBar';
import { JobLogs } from './JobLogs';
import { Breadcrumb } from './Breadcrumb';

interface AgentConfigProps {
  projectId: number;
  agentId: string | 'new';
  agentType?: string;
}

export function AgentConfig({ projectId, agentId, agentType }: AgentConfigProps) {
  const { user, token } = useAuth();
  const isNewAgent = agentId === 'new';

  // Form state
  const [engine, setEngine] = useState<AgentEngine>('pr_agent_v0.29');
  const [type, setType] = useState<AgentType>(agentType as AgentType || 'mr-describer');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [provider, setProvider] = useState('anthropic');
  const [model, setModel] = useState('');
  const [tokenValue, setTokenValue] = useState('');
  const [prompt, setPrompt] = useState('');
  const [externalUrl, setExternalUrl] = useState('');
  const [enabled, setEnabled] = useState(false);

  // Available agent types from placeholders
  const [availableTypes, setAvailableTypes] = useState<AgentType[]>([]);

  // Project data
  const [project, setProject] = useState<Project | null>(null);

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!token || !user) return;

    setIsLoading(true);
    setError(null);

    if (isNewAgent) {
      // Load placeholder data for new agent
      getAgentPlaceholders(projectId, token)
        .then((response) => {
          // Get available agent types from placeholders
          const types = response.agents.map(a => a.type);
          setAvailableTypes(types);

          // Set default type if not provided
          if (!agentType && types.length > 0) {
            setType(types[0]);
          }

          const placeholder = response.agents.find(a => a.type === (agentType || types[0]));
          if (placeholder) {
            setEngine(placeholder.engine);
            setName(placeholder.name);
            setDescription(placeholder.description);
            setProvider(placeholder.config.provider);
            setModel(placeholder.config.model);
            setTokenValue(''); // Always empty for new agents
            setPrompt(placeholder.config.prompt || '');
            setExternalUrl(placeholder.config.external_url || '');
            setEnabled(true); // Always enabled by default for new agents
          }
        })
        .catch((err) => {
          console.error('Failed to load placeholder:', err);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      // Load existing agent data
      getAgent(projectId, agentId, token)
        .then((response) => {
          const agent = response.agent;
          setEngine(agent.engine);
          setType(agent.type);
          setName(agent.name);
          setDescription(agent.description);
          setProvider(agent.config.provider);
          setModel(agent.config.model);
          setTokenValue(agent.config.token);
          setPrompt(agent.config.prompt || '');
          setExternalUrl(agent.config.external_url || '');
          setEnabled(agent.enabled);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : 'Failed to load agent');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [projectId, agentId, token, user, isNewAgent, agentType]);

  useEffect(() => {
    if (!token || !user) return;

    getProject(projectId, token)
      .then((response) => {
        setProject(response.project);
      })
      .catch((err) => {
        console.error('Failed to load project:', err);
      });
  }, [projectId, token, user]);

  const handleBack = () => {
    window.location.href = `/project/${projectId}`;
  };

  const formatAgentTypeLabel = (agentType: AgentType): string => {
    return agentType.split('-').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!name.trim()) errors.name = 'Name is required';
    if (!description.trim()) errors.description = 'Description is required';
    if (!model.trim()) errors.model = 'Model is required';
    if (!tokenValue.trim()) errors.token = 'Token is required';
    if (engine === 'external' && !externalUrl.trim()) {
      errors.externalUrl = 'External URL is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !token) return;

    setIsSaving(true);
    setError(null);

    const agentData: Partial<Agent> = {
      type,
      engine,
      name,
      description,
      enabled,
      config: {
        provider,
        model,
        token: tokenValue,
        prompt: prompt || null,
        external_url: engine === 'external' ? externalUrl : null,
      },
    };

    try {
      if (isNewAgent) {
        await createAgent(projectId, agentData, token);
      } else {
        await updateAgent(projectId, agentId, agentData, token);
      }
      // Redirect back to project page
      window.location.href = `/project/${projectId}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save agent');
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <Navbar />

      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <Breadcrumb items={[
              { label: 'Dashboard', href: '/', icon: <Home size={14} /> },
              { label: project?.name || 'Project', href: `/project/${projectId}`, icon: <Folder size={14} /> },
              { label: isNewAgent ? 'Create Agent' : (name || 'Configure Agent'), icon: <Bot size={14} /> },
            ]} />
            {/*<Link
              href={`/project/${projectId}`}
              className="button is-text mb-4"
            >
              <span className="icon">
                <ArrowLeft size={16} />
              </span>
              <span>Back to Project</span>
            </Link>*/}

            <h1 className="title">{isNewAgent ? 'Create Agent' : 'Configure Agent'}</h1>

            {isLoading && (
              <div className="has-text-centered py-6">
                <p>Loading...</p>
              </div>
            )}

            {error && (
              <div className="notification is-danger is-light">
                {error}
              </div>
            )}

            {!isLoading && (
              <form onSubmit={handleSubmit}>
                {/* Engine Selection Dropdown */}
                <div className="field">
                  <label className="label">Agent Engine</label>
                  <div className="control">
                    <div className="select is-fullwidth">
                      <select
                        value={engine}
                        onChange={(e) => setEngine(e.target.value as AgentEngine)}
                        disabled={!isNewAgent}
                      >
                        <option value="pr_agent_v0.29">PR Agent v0.29</option>
                        <option value="external">External</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Agent Type */}
                <div className="field">
                  <label className="label">Agent Type</label>
                  <div className="control">
                    <div className="select is-fullwidth">
                      <select
                        value={type}
                        onChange={(e) => setType(e.target.value as AgentType)}
                        disabled={true}
                      >
                        {isNewAgent && availableTypes.length > 0 ? (
                          availableTypes.map((agentType) => (
                            <option key={agentType} value={agentType}>
                              {formatAgentTypeLabel(agentType)}
                            </option>
                          ))
                        ) : (
                          <>
                            <option value="mr-describer">MR Describer</option>
                            <option value="mr-reviewer">MR Reviewer</option>
                          </>
                        )}
                      </select>
                    </div>
                  </div>
                </div>

                {/* External URL (only for external engine) */}
                {engine === 'external' && (
                  <div className="field">
                    <label className="label">External URL</label>
                    <div className="control">
                      <input
                        className={`input ${validationErrors.externalUrl ? 'is-danger' : ''}`}
                        type="url"
                        value={externalUrl}
                        onChange={(e) => setExternalUrl(e.target.value)}
                        placeholder="https://example.com/webhook"
                      />
                    </div>
                    {validationErrors.externalUrl && (
                      <p className="help is-danger">{validationErrors.externalUrl}</p>
                    )}
                  </div>
                )}

                {/* Agent Name */}
                <div className="field">
                  <label className="label">Name</label>
                  <div className="control">
                    <input
                      className={`input ${validationErrors.name ? 'is-danger' : ''}`}
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Agent name"
                    />
                  </div>
                  {validationErrors.name && (
                    <p className="help is-danger">{validationErrors.name}</p>
                  )}
                </div>

                {/* Agent Description */}
                <div className="field">
                  <label className="label">Description</label>
                  <div className="control">
                    <textarea
                      className={`textarea ${validationErrors.description ? 'is-danger' : ''}`}
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Agent description"
                      rows={3}
                    />
                  </div>
                  {validationErrors.description && (
                    <p className="help is-danger">{validationErrors.description}</p>
                  )}
                </div>

                {/* Provider */}
                <div className="field">
                  <label className="label">AI Provider</label>
                  <div className="control">
                    <div className="select is-fullwidth">
                      <select
                        value={provider}
                        onChange={(e) => setProvider(e.target.value)}
                      >
                        <option value="anthropic">Anthropic</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Model */}
                <div className="field">
                  <label className="label">AI Model</label>
                  <div className="control">
                    <input
                      className={`input ${validationErrors.model ? 'is-danger' : ''}`}
                      type="text"
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      placeholder="claude-3-5-sonnet-20241022"
                    />
                  </div>
                  {validationErrors.model && (
                    <p className="help is-danger">{validationErrors.model}</p>
                  )}
                </div>

                {/* Token */}
                <div className="field">
                  <label className="label">AI Token</label>
                  <div className="control">
                    <input
                      className={`input ${validationErrors.token ? 'is-danger' : ''}`}
                      type="password"
                      value={tokenValue}
                      onChange={(e) => setTokenValue(e.target.value)}
                      placeholder="API token"
                    />
                  </div>
                  {validationErrors.token && (
                    <p className="help is-danger">{validationErrors.token}</p>
                  )}
                </div>

                {/* Prompt */}
                <div className="field">
                  <label className="label">
                    Custom Prompt <span className="has-text-grey-light">(optional)</span>
                  </label>
                  <div className="control">
                    <textarea
                      className="textarea"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Custom prompt for the agent"
                      rows={5}
                    />
                  </div>
                </div>

                {/* Enabled Checkbox */}
                <div className="field">
                  <div className="control">
                    <label className="checkbox">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={(e) => setEnabled(e.target.checked)}
                      />
                      {' '}Enabled
                    </label>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="field is-grouped">
                  <div className="control">
                    <button
                      type="submit"
                      className={`button is-link ${isSaving ? 'is-loading' : ''}`}
                      disabled={isSaving}
                    >
                      <span className="icon">
                        <Save size={16} />
                      </span>
                      <span>{isNewAgent ? 'Create Agent' : 'Save Changes'}</span>
                    </button>
                  </div>
                  <div className="control">
                    <button
                      type="button"
                      className="button is-light"
                      onClick={handleBack}
                      disabled={isSaving}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>

          {!isNewAgent && !isLoading && (
            <div style={{ maxWidth: '800px', margin: '20px auto 0' }}>
              <JobLogs projectId={projectId} agentId={agentId} />
            </div>
          )}
        </div>
      </section>
    </>
  );
}
