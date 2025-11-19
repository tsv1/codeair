import { useState } from 'react';
import { useAuth } from './AuthContext';
import { searchProjects, type Project } from './api';
import { Search } from 'lucide-react';
import { Navbar } from './Navbar';

export function Dashboard() {
  const { user, token } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Project[] | null>(null);
  const [botUsername, setBotUsername] = useState<string>('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  if (!user) {
    return null;
  }

  const handleSearch = async () => {
    if (!searchQuery.trim() || !token) return;

    setIsSearching(true);
    setSearchError(null);

    try {
      const response = await searchProjects(searchQuery, token);
      setSearchResults(response.items);
      setBotUsername(response.bot_user.username);
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : 'Failed to search projects');
      setSearchResults(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <>
      <Navbar />

      <section className="section">
        <div className="container">
          <div className="box" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h1 className="title">Search Projects</h1>
            <p className="subtitle">Search for GitLab projects to enable AI code review</p>

            <div className="field has-addons">
              <div className="control is-expanded">
                <input
                  className="input"
                  type="text"
                  placeholder="Search projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isSearching}
                />
              </div>
              <div className="control">
                <button
                  className={`button is-link ${isSearching ? 'is-loading' : ''}`}
                  onClick={handleSearch}
                  disabled={isSearching || !searchQuery.trim()}
                >
                  <span className="icon">
                    <Search size={16} />
                  </span>
                  <span>Search</span>
                </button>
              </div>
            </div>

            {searchError && (
              <div className="notification is-danger is-light mt-4">
                {searchError}
              </div>
            )}

            {searchResults !== null && searchResults.length === 0 && (
              <div className="notification is-warning is-light mt-4">
                <p className="has-text-weight-bold mb-2">No projects found</p>
                <p className="mb-2">Can't find your project? Make sure:</p>
                <ul style={{ marginLeft: '1.5rem' }}>
                  <li>Check for typos in your search query</li>
                  <li>Add <strong>{botUsername || 'codeair'}</strong> user with Maintainer role to your project</li>
                </ul>
              </div>
            )}

            {searchResults !== null && searchResults.length > 0 && (
              <div className="mt-4">
                {searchResults.map((project) => (
                  <div key={project.id} className="box mb-3">
                    <article className="media">
                      <figure className="media-left">
                        <p className="image is-64x64">
                          {project.avatar_url ? (
                            <img src={project.avatar_url} alt={project.name} />
                          ) : (
                            <div
                              style={{
                                width: '64px',
                                height: '64px',
                                backgroundColor: '#f5f5f5',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '4px',
                              }}
                            >
                              <span style={{ fontSize: '24px', color: '#999' }}>
                                {project.name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          )}
                        </p>
                      </figure>
                      <div className="media-content">
                        <div className="content">
                          <p>
                            <a
                              href={`/project/${project.id}`}
                              onClick={(e) => {
                                e.preventDefault();
                                window.location.href = `/project/${project.id}`;
                              }}
                              className="has-text-weight-bold"
                            >
                              {project.name_with_namespace}
                            </a>
                            <br />
                            {project.description && (
                              <span className="has-text-grey">{project.description}</span>
                            )}
                          </p>
                        </div>
                      </div>
                    </article>
                  </div>
                ))}

                <div className="notification is-info is-light mt-4">
                  <p className="is-size-7">
                    Can't find your project? Add <strong>{botUsername || 'codeair'}</strong> user with Maintainer role to make it accessible.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
