# CodeAir

A code analysis and review platform that automatically processes merge requests using AI agents.

## Quick Start

### Prerequisites

- Docker
- PostgreSQL database
- GitLab instance (local or cloud)

### Running with Docker

```bash
docker run -p 8080:80 --env-file .env ghcr.io/tsv1/codeair:0.0.1
```

### Environment Configuration

Create a `.env` file with the following variables:
```bash
# Application
APP_ENCRYPTION_KEY=<your-32-char-encryption-key>
APP_WEBHOOK_BASE_URL=http://localhost:8080
JWT_SECRET_KEY=<your-jwt-secret>

# Database
DATABASE_URL=postgresql://codeair:dev_hcxrh66fn4@localhost:6432/codeair

# GitLab Bot
CODEAIR_BOT_TOKEN=glpat-<your-gitlab-bot-token>

# GitLab OAuth
GITLAB_API_BASE_URL=http://localhost:8000
GITLAB_OAUTH_CLIENT_ID=<your-oauth-client-id>
GITLAB_OAUTH_CLIENT_SECRET=gloas-<your-oauth-client-secret>
GITLAB_OAUTH_REDIRECT_URI=http://localhost:8080/auth/callback
```
