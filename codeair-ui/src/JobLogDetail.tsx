import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getJobLog, getProject, getAgent, type JobLogResponse, type Project, type Agent } from './api';
import { ExternalLink, Home, Folder, Bot, FileText } from 'lucide-react';
import { Navbar } from './NavBar';
import { AnsiOutput } from './AnsiOutput';
import { Breadcrumb } from './Breadcrumb';

interface JobLogDetailProps {
  projectId: number;
  agentId: string;
  jobId: number;
}

export function JobLogDetail({ projectId, agentId, jobId }: JobLogDetailProps) {
  const { user, token } = useAuth();
  const [log, setLog] = useState<JobLogResponse | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [agent, setAgent] = useState<Agent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !user) return;

    setIsLoading(true);
    setError(null);

    getJobLog(projectId, agentId, jobId, token)
      .then((response) => {
        setLog(response);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load run log');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [projectId, agentId, jobId, token, user]);

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

  useEffect(() => {
    if (!token || !user) return;

    getAgent(projectId, agentId, token)
      .then((response) => {
        setAgent(response.agent);
      })
      .catch((err) => {
        console.error('Failed to load agent:', err);
      });
  }, [projectId, agentId, token, user]);

  const extractMrId = (mrUrl: string): string => {
    const match = mrUrl.match(/merge_requests\/(\d+)/);
    return match ? match[1] : 'N/A';
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (elapsedMs: number | null): string => {
    if (elapsedMs === null) return 'N/A';
    if (elapsedMs < 1000) return `${elapsedMs}ms`;
    const seconds = Math.floor(elapsedMs / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusClass = (createdAt: string | null, endedAt: string | null): string => {
    if (createdAt === null && endedAt === null) return 'tag is-light';
    if (createdAt !== null && endedAt === null) return 'tag is-light';
    return 'tag is-success';
  };

  const getStatusText = (createdAt: string | null, endedAt: string | null): string => {
    if (createdAt === null && endedAt === null) return 'Pending';
    if (createdAt !== null && endedAt === null) return 'Running';
    return 'Finished';
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <Navbar />

      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <Breadcrumb items={[
              { label: 'Dashboard', href: '/', icon: <Home size={14} /> },
              { label: project?.name || 'Project', href: `/project/${projectId}`, icon: <Folder size={14} /> },
              { label: agent?.name || 'Agent', href: `/project/${projectId}/agents/${agentId}`, icon: <Bot size={14} /> },
              { label: `Run #${jobId}`, icon: <FileText size={14} /> },
            ]} />
            {/*<Link
              href={`/project/${projectId}/agents/${agentId}`}
              className="button is-text mb-4"
            >
              <span className="icon">
                <ArrowLeft size={16} />
              </span>
              <span>Back to Agent</span>
            </Link>*/}

            <h1 className="title">Run Log Details</h1>

            {isLoading && (
              <div className="has-text-centered py-6">
                <p>Loading run log...</p>
              </div>
            )}

            {error && (
              <div className="notification is-danger is-light">
                {error}
              </div>
            )}

            {log && !isLoading && (
              <div>
                {/* Job Info Section */}
                <div className="box mb-4">
                  <h2 className="title is-5 mb-3">Run Information</h2>
                  <div className="columns is-multiline">
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Run ID</label>
                        <p className="has-text-weight-semibold">{log.job_id}</p>
                      </div>
                    </div>
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Merge Request</label>
                        <p>
                          <a
                            href={log.mr_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="has-text-link"
                          >
                            <span>#{extractMrId(log.mr_url)}</span>
                            <span className="icon is-small ml-1">
                              <ExternalLink size={14} />
                            </span>
                          </a>
                        </p>
                      </div>
                    </div>
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Started At</label>
                        <p>{formatDate(log.started_at)}</p>
                      </div>
                    </div>
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Ended At</label>
                        <p>{formatDate(log.ended_at)}</p>
                      </div>
                    </div>
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Duration</label>
                        <p>{formatDuration(log.elapsed_ms)}</p>
                      </div>
                    </div>
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Status</label>
                        <p>
                          <span className={getStatusClass(log.created_at, log.ended_at)}>
                            {getStatusText(log.created_at, log.ended_at)}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stdout Section */}
                <div className="box mb-4">
                  <h2 className="title is-5 mb-3">Standard Output (stdout)</h2>
                  {log.stdout ? (
                    <AnsiOutput content={log.stdout} />
                  ) : (
                    <div className="notification is-light">
                      <p className="has-text-grey-light">No stdout output</p>
                    </div>
                  )}
                </div>

                {/* Stderr Section */}
                <div className="box">
                  <h2 className="title is-5 mb-3">Standard Error (stderr)</h2>
                  {log.stderr ? (
                    <AnsiOutput
                      content={log.stderr}
                      border="1px solid #f14668"
                    />
                  ) : (
                    <div className="notification is-light">
                      <p className="has-text-grey-light">No stderr output</p>
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
