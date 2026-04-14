# Creator-AI Setup Guide

Complete installation and configuration guide to get Creator-AI running.

## Prerequisites

- **Python 3.10+** (download from python.org)
- **Git** (download from git-scm.com)
- **GitHub account** (for Actions scheduling)
- **Platform API credentials** (YouTube, TikTok, Instagram, Twitter)
- **Optional but recommended:**
  - Ollama (for local LLM hosting)
  - CUDA/GPU (for faster image generation)

## Local Installation

### 1. Clone Repository

```bash
git clone https://github.com/morgan9hips-sketch/creator-ai.git
cd creator-ai
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your favorite editor
```

## Configuration

### Essential Configuration

Edit `.env` file with your values:

```env
# System
ENVIRONMENT=development
DEBUG=True

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AI Models
OLLAMA_API_URL=http://localhost:11434
HUGGINGFACE_API_KEY=hf_your_token

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=creator-ai-content

# Platform APIs (at least one required to post)
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CHANNEL_ID=UCxxxxxx
TIKTOK_CLIENT_KEY=your-key
TIKTOK_CLIENT_SECRET=your-secret
META_ACCESS_TOKEN=your-token
TWITTER_BEARER_TOKEN=your-token
```

## Service Setup

### Option 1: Self-Hosted (Recommended for Development)

#### Ollama Setup (for local LLM)

1. Download from https://ollama.ai
2. Install and run
3. Pull a model:
   ```bash
   ollama pull mistral:7b  # or llama2:7b
   ```
4. Ollama will run on `http://localhost:11434` by default

### Option 2: Cloud Hosting (Recommended for Production)

#### Using HuggingFace Spaces

1. Sign up at huggingface.co
2. Create API token: huggingface.co/settings/tokens
3. Add to `.env`:
   ```env
   HUGGINGFACE_API_KEY=hf_your_token_here
   ```

#### Using AWS Services

1. Create IAM user with S3 permissions
2. Create S3 bucket for content
3. Get access keys and add to `.env`

#### Using Supabase

1. Sign up at supabase.com
2. Create project and get connection details
3. Add to `.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

## Platform Setup

### YouTube

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON
6. Run authentication flow

### TikTok

1. Go to [TikTok Developer](https://developers.tiktok.com)
2. Create app
3. Request Creator API access
4. Get Client Key and Secret
5. Generate access token

### Instagram (via Meta)

1. Go to [Meta Developers](https://developers.facebook.com)
2. Create app
3. Get App ID and App Secret
4. Generate access token with Instagram content access

### Twitter/X

1. Go to [X Developer Portal](https://developer.twitter.com)
2. Create app
3. Generate API keys and access tokens
4. Request elevated access if needed

## Running Creator-AI

### CLI Mode (Interactive)

```bash
python main.py cli
# or
python main.py --cli
```

This performs:

1. Content generation (script, images, audio)
2. Saves to database
3. Displays results

### HTTP Server Mode (API)

```bash
python main.py server
# or
python main.py --server
```

Server runs on `http://localhost:8000` (configurable via `APP_PORT`)

### Scheduler Mode (Automated)

```bash
python main.py scheduler
```

Generates content automatically on schedule (default: Friday 8 PM UTC)

### Health Check

```bash
python main.py health
```

Verifies all services are operational.

## VS Code Debugging

1. Install extensions:
   - Python
   - Pylance
   - AI Toolkit

2. Open VS Code command palette: `Ctrl+Shift+P`

3. Select debug configuration:
   - "Debug Creator-AI HTTP Server" - for testing API
   - "Debug Creator-AI CLI" - for testing pipeline
   - "Debug Tests" - for running tests

4. Press F5 to start debugging

5. Open Agent Inspector: https://localhost:8088 (if running in HTTP mode)

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or use netstat on Windows

# Kill process
kill -9 <PID>
```

### Database Connection Failed

```bash
# Check connection string
echo $DATABASE_URL

# Verify Supabase is accessible
curl https://your-project.supabase.co
```

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
# Or run: ollama serve
```

### Missing API Keys

```bash
# Verify .env file has all required keys
grep -E "API_KEY|ACCESS_TOKEN|CLIENT" .env

# Make sure you're using correct format
# Not: YOUTUBE_API_KEY = "key"   (wrong - spaces)
# But: YOUTUBE_API_KEY=key       (correct)
```

## Next Steps

1. **Generate first content:** `python main.py cli`
2. **Test distribution:** Configure platform APIs and run
3. **Schedule automated runs:** Set up GitHub Actions
4. **Deploy to cloud:** Reference [Deployment Guide](DEPLOYMENT.md)
5. **Monitor performance:** Check analytics dashboard

## Support

- GitHub Issues: github.com/morgan9hips-sketch/creator-ai/issues
- Documentation: docs/ folder
- Examples: examples/ folder

## Performance Tips

- Use GPU for faster image generation: Set `TTS_DEVICE=cuda`
- Cache AI model outputs to reduce API calls
- Batch content generation (generate 5+ at once)
- Use free tier services during development, paid during production scaling
