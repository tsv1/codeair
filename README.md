# CodeAir

**AI-Powered Code Review Platform for GitLab**

## Overview

CodeAir is a web application that brings AI-powered automation to your GitLab merge request workflow. It enables teams to configure intelligent agents that automatically generate merge request descriptions and provide code review suggestions using Anthropic Claude models.

## Key Features

### 🔍 Project Discovery
Search and connect your GitLab projects to CodeAir. Simply add the CodeAir bot user as a Maintainer to your repository to enable AI capabilities.

### 🤖 AI Agents
Configure specialized agents for your projects:

- **📝 MR Description Writer** — Automatically generates comprehensive descriptions for merge requests, summarizing changes, impact, and context.

- **🔍 MR Code Reviewer** — Analyzes code changes and provides inline suggestions, identifying potential bugs, improvements, and best practices.

### ⚙️ Flexible Configuration
- Customize agent behavior with custom prompts
- Enable/disable agents per project
- Support for external webhook engines for custom integrations

### 📊 Job Monitoring
- Track agent execution history with detailed run logs
- View stdout/stderr output for debugging
- Monitor execution duration and status

## Architecture

| Component | Technology |
|-----------|------------|
| Frontend | React, TypeScript, Bulma CSS |
| Backend API | Python, Litestar |
| Worker | Async Python |
| AI Engine | [PR-Agent v0.29](https://github.com/qodo-ai/pr-agent/tree/v0.29) (last Apache 2.0 licensed version) |
| Authentication | GitLab OAuth |
| AI Providers | Anthropic Claude |

## Setup

### Prerequisites

1. **GitLab Bot Account** — Create a dedicated GitLab user for CodeAir and generate a Personal Access Token with `api` scope
2. **GitLab OAuth Application** — Register an OAuth application in GitLab with `read_user` scope
3. **Anthropic API Key** — Obtain from [console.anthropic.com](https://console.anthropic.com) (configured per-agent in the UI)

### Quick Start with Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/tsv1/codeair.git
cd codeair
```

2. Create a `.env` file:
```bash
# Application
APP_ENCRYPTION_KEY=<32-character-random-string>
APP_WEBHOOK_BASE_URL=https://your-codeair-domain.com
JWT_SECRET_KEY=<64-character-random-string>

# Database
DATABASE_URL=postgresql://codeair:dev_aQUCVlDkUk@postgres:5432/codeair

# GitLab Bot
CODEAIR_BOT_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# GitLab OAuth
GITLAB_API_BASE_URL=https://gitlab.com  # or your self-hosted GitLab URL
GITLAB_OAUTH_CLIENT_ID=<your-oauth-client-id>
GITLAB_OAUTH_CLIENT_SECRET=gloas-<your-oauth-client-secret>
GITLAB_OAUTH_REDIRECT_URI=https://your-codeair-domain.com/auth/callback
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access CodeAir at `http://localhost:8080`

### Alternative Deployment

The CodeAir image (`ghcr.io/tsv1/codeair:0.0.6`) can be deployed anywhere (Kubernetes, VM, etc.) by running two containers with the same environment variables.

## How It Works

1. **Authenticate** with your GitLab account
2. **Search** for projects where the bot has access
3. **Configure** AI agents with your API keys and preferences
4. **Receive** automatic descriptions and reviews on new merge requests

---

*CodeAir streamlines your code review process, helping teams ship better code faster.*
