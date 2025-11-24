const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export interface User {
  id: number;
  username: string;
  name: string;
  web_url: string;
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

export interface AgentConfig {
  provider: string;
  model: string;
  token: string;
  prompt?: string | null;
  external_url?: string | null;
}

export type AgentEngine = 'pr_agent_v0.29' | 'external';
export type AgentType = 'mr-describer' | 'mr-reviewer';

export interface Agent {
  id: string;
  type: AgentType;
  engine: AgentEngine;
  name: string;
  description: string;
  enabled: boolean;
  config: AgentConfig;
  created_at: string;
  updated_at: string;
}

export interface AgentsListResponse {
  total: number;
  agents: Agent[];
}

export interface AgentResponse {
  agent: Agent;
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

export async function getAgents(projectId: number, token: string): Promise<AgentsListResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get agents');
  }
  return response.json();
}

export async function getAgentPlaceholders(projectId: number, token: string): Promise<AgentsListResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents/placeholders`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get agent placeholders');
  }
  return response.json();
}

export async function getAgent(projectId: number, agentId: string, token: string): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents/${agentId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get agent');
  }
  return response.json();
}

export async function createAgent(projectId: number, agent: Partial<Agent>, token: string): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agent),
  });
  if (!response.ok) {
    throw new Error('Failed to create agent');
  }
  return response.json();
}

export async function updateAgent(projectId: number, agentId: string, agent: Partial<Agent>, token: string): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents/${agentId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agent),
  });
  if (!response.ok) {
    throw new Error('Failed to update agent');
  }
  return response.json();
}

export interface JobLogResponse {
  job_id: number;
  mr_url: string;
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
  exit_code: number | null;
  stdout: string | null;
  stderr: string | null;
  elapsed_ms: number | null;
}

export interface AgentLogsResponse {
  total: number;
  logs: JobLogResponse[];
}

export async function getAgentLogs(projectId: number, agentId: string, token: string, limit: number = 10): Promise<AgentLogsResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents/${agentId}/logs?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get agent logs');
  }
  return response.json();
}

export async function getJobLog(projectId: number, agentId: string, jobId: number, token: string): Promise<JobLogResponse> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}/agents/${agentId}/logs/${jobId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to get job log');
  }
  return response.json();
}
