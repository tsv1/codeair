import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getJobLog, type JobLogResponse } from './api';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { Navbar } from './Navbar';

interface JobLogDetailProps {
  projectId: number;
  agentId: string;
  jobId: number;
}

export function JobLogDetail({ projectId, agentId, jobId }: JobLogDetailProps) {
  const { user, token } = useAuth();
  const [log, setLog] = useState<JobLogResponse | null>(null);
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
        setError(err instanceof Error ? err.message : 'Failed to load job log');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [projectId, agentId, jobId, token, user]);

  const handleBack = () => {
    window.location.href = `/project/${projectId}/agents/${agentId}`;
  };

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

  const getStatusClass = (exitCode: number | null): string => {
    if (exitCode === null) return 'tag is-light';
    return exitCode === 0 ? 'tag is-success' : 'tag is-danger';
  };

  const getStatusText = (exitCode: number | null): string => {
    if (exitCode === null) return 'Running';
    return exitCode === 0 ? 'Success' : `Failed (Exit Code: ${exitCode})`;
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
            <button className="button is-text mb-4" onClick={handleBack}>
              <span className="icon">
                <ArrowLeft size={16} />
              </span>
              <span>Back to Agent</span>
            </button>

            <h1 className="title">Job Log Details</h1>

            {isLoading && (
              <div className="has-text-centered py-6">
                <p>Loading job log...</p>
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
                  <h2 className="title is-5 mb-3">Job Information</h2>
                  <div className="columns is-multiline">
                    <div className="column is-half">
                      <div className="field">
                        <label className="label is-small">Job ID</label>
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
                        <label className="label is-small">Created At</label>
                        <p>{formatDate(log.created_at)}</p>
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
                          <span className={getStatusClass(log.exit_code)}>
                            {getStatusText(log.exit_code)}
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
                    <div
                      style={{
                        maxHeight: '400px',
                        overflow: 'auto',
                        backgroundColor: '#f5f5f5',
                        padding: '1rem',
                        borderRadius: '4px',
                      }}
                    >
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {log.stdout}
                      </pre>
                    </div>
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
                    <div
                      style={{
                        maxHeight: '400px',
                        overflow: 'auto',
                        backgroundColor: '#fff5f5',
                        padding: '1rem',
                        borderRadius: '4px',
                        border: '1px solid #f14668',
                      }}
                    >
                      <pre
                        style={{
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          color: '#cc0f35',
                        }}
                      >
                        {log.stderr}
                      </pre>
                    </div>
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
