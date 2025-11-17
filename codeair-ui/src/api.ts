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
