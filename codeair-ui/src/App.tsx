import { useAuth } from './AuthContext';
import { Login } from './Login';
import { Callback } from './Callback';
import { Dashboard } from './Dashboard';
import { ProjectView } from './ProjectView';
import { AgentConfig } from './AgentConfig';
import { JobLogDetail } from './JobLogDetail';

function App() {
  const { user, isLoading } = useAuth();
  const path = window.location.pathname;

  if (isLoading) {
    return (
      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <p className="has-text-centered">Loading...</p>
          </div>
        </div>
      </section>
    );
  }

  // Handle OAuth callback
  if (path === '/auth/callback') {
    return <Callback />;
  }

  // Show login if not authenticated
  if (!user) {
    return <Login />;
  }

  // Handle job log detail route: /project/{id}/agents/{agentId}/logs/{jobId}
  const jobLogMatch = path.match(/^\/project\/(\d+)\/agents\/([a-f0-9-]+)\/logs\/(\d+)$/);
  if (jobLogMatch) {
    const projectId = parseInt(jobLogMatch[1], 10);
    const agentId = jobLogMatch[2];
    const jobId = parseInt(jobLogMatch[3], 10);
    return <JobLogDetail projectId={projectId} agentId={agentId} jobId={jobId} />;
  }

  // Handle agent configuration routes: /project/{id}/agents/{new|uuid}
  const agentConfigMatch = path.match(/^\/project\/(\d+)\/agents\/(new|[a-f0-9-]+)$/);
  if (agentConfigMatch) {
    const projectId = parseInt(agentConfigMatch[1], 10);
    const agentId = agentConfigMatch[2];
    const searchParams = new URLSearchParams(window.location.search);
    const agentType = searchParams.get('type') || undefined;
    return <AgentConfig projectId={projectId} agentId={agentId} agentType={agentType} />;
  }

  // Handle project view route
  const projectMatch = path.match(/^\/project\/(\d+)$/);
  if (projectMatch) {
    const projectId = parseInt(projectMatch[1], 10);
    return <ProjectView projectId={projectId} />;
  }

  // Show dashboard if authenticated
  return <Dashboard />;
}

export default App;
