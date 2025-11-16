import { useAuth } from './AuthContext';
import { Login } from './Login';
import { Callback } from './Callback';
import { Dashboard } from './Dashboard';

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

  // Show dashboard if authenticated
  return <Dashboard />;
}

export default App;
