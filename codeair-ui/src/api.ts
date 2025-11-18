const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export interface User {
  id: number;
  username: string;
  name: string;
  avatar_url?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginUrlResponse {
  authorization_url: string;
}

export interface Project {
  id: number;
  name: string;
  name_with_namespace: string;
  path: string;
  path_with_namespace: string;
  description?: string;
  visibility: string;
  web_url: string;
  created_at: string;
  last_activity_at: string;
  avatar_url?: string;
}

export interface ProjectSearchResponse {
  total: number;
  items: Project[];
  bot_user: User;
}

export async function getLoginUrl(): Promise<LoginUrlResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/gitlab/authorize`);
  if (!response.ok) {
    throw new Error('Failed to get login URL');
  }
  return response.json();
}

export async function handleCallback(code: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/gitlab/callback?code=${code}`);
  if (!response.ok) {
    throw new Error('Failed to authenticate');
  }
  return response.json();
}

export async function logout(token: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to logout');
  }
}

export interface ProjectDetailResponse {
  project: Project;
}

export async function searchProjects(query: string, token: string): Promise<ProjectSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/search?q=${encodeURIComponent(query)}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to search projects');
  }
  return response.json();
}

export async function getProject(projectId: number, token: string): Promise<ProjectDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get project');
  }
  return response.json();
}
