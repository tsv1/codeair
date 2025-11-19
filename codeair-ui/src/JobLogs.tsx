import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getAgentLogs, type JobLogResponse } from './api';

interface JobLogsProps {
  projectId: number;
  agentId: string;
}

export function JobLogs({ projectId, agentId }: JobLogsProps) {
  const { token } = useAuth();
  const [logs, setLogs] = useState<JobLogResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    setIsLoading(true);
    setError(null);

    getAgentLogs(projectId, agentId, token, 10)
      .then((response) => {
        setLogs(response.logs);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load logs');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [projectId, agentId, token]);

  const extractMrId = (mrUrl: string): string => {
    // Extract MR ID from URL like: https://gitlab.com/project/repo/-/merge_requests/123
    const match = mrUrl.match(/merge_requests\/(\d+)/);
    return match ? match[1] : 'N/A';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getExitCodeClass = (exitCode: number | null): string => {
    if (exitCode === null) return 'tag is-light';
    return exitCode === 0 ? 'tag is-success' : 'tag is-danger';
  };

  const getExitCodeText = (exitCode: number | null): string => {
    if (exitCode === null) return 'Running';
    return exitCode === 0 ? 'Success' : `Failed (${exitCode})`;
  };

  if (isLoading) {
    return (
      <div className="box">
        <h2 className="title is-5">Recent Jobs</h2>
        <div className="has-text-centered py-4">
          <p>Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="box">
        <h2 className="title is-5">Recent Jobs</h2>
        <div className="notification is-danger is-light">
          {error}
        </div>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="box">
        <h2 className="title is-5">Recent Jobs</h2>
        <div className="notification is-info is-light">
          No jobs have been executed yet.
        </div>
      </div>
    );
  }

  return (
    <div className="box">
      <h2 className="title is-5">Recent Jobs</h2>
      <div className="table-container">
        <table className="table is-fullwidth is-striped is-hoverable">
          <thead>
            <tr>
              <th>Job ID</th>
              <th>MR ID</th>
              <th>Created At</th>
              <th>Ended At</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.job_id}>
                <td>
                  <a
                    href={`/project/${projectId}/agents/${agentId}/logs/${log.job_id}`}
                    onClick={(e) => {
                      e.preventDefault();
                      window.location.href = `/project/${projectId}/agents/${agentId}/logs/${log.job_id}`;
                    }}
                    className="has-text-link"
                  >
                    {log.job_id}
                  </a>
                </td>
                <td>
                  <a
                    href={log.mr_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="has-text-link"
                  >
                    #{extractMrId(log.mr_url)}
                  </a>
                </td>
                <td>{formatDate(log.created_at)}</td>
                <td>{log.ended_at ? formatDate(log.ended_at) : '-'}</td>
                <td>
                  <span className={getExitCodeClass(log.exit_code)}>
                    {getExitCodeText(log.exit_code)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
