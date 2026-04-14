# Creator-AI Quick Reference & Cheat Sheet

Quick commands and configurations for daily use.

## Most-Used Commands

### Content Generation

```bash
# Generate 1 content piece (interactive)
python main.py cli

# Generate 5 pieces for motivational niche
python main.py cli --niche motivational --count 5

# Generate with specific platform focus
python main.py cli --platforms tiktok instagram_reels

# Generate and use specific hook pattern
python main.py cli --hook-style curiosity_gap
```

### Server & Testing

```bash
# Start HTTP server (API mode)
python main.py server

# Health check (verify all services)
python main.py health

# Run with verbose output
python main.py --verbose

# Scheduler mode (weekly automation)
python main.py scheduler
```

### Development & Debugging

```bash
# Run with debug logging
DEBUG=True python main.py cli

# Debug HTTP server with VS Code
F5  # In VS Code, with debug config active

# Run tests
pytest tests/ -v

# Format code
black src/

# Lint code
flake8 src/
```

### Docker (For Cloud)

```bash
# Build Docker image
docker build -t creator-ai:latest .

# Run container locally
docker-compose up -d

# View logs
docker-compose logs -f creator-ai

# Stop containers
docker-compose down

# Push to registry (if using container registry)
docker tag creator-ai:latest ghcr.io/username/creator-ai:latest
docker push ghcr.io/username/creator-ai:latest
```

---

## Environment Variables Cheat Sheet

### Minimal Setup (Testing)

```env
ENVIRONMENT=development
DEBUG=True
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
HUGGINGFACE_API_KEY=hf_token
USE_MOCK_APIS=true  # For testing without real APIs
```

### Full Production Setup

```env
# System
ENVIRONMENT=production
DEBUG=False
APP_PORT=8000

# Database
SUPABASE_URL=your-url
SUPABASE_KEY=your-key

# Storage
AWS_ACCESS_KEY_ID=key
AWS_SECRET_ACCESS_KEY=secret
S3_BUCKET_NAME=creator-ai-content

# AI Models
OLLAMA_API_URL=http://localhost:11434
HUGGINGFACE_API_KEY=hf_token

# Platforms (use real tokens for production)
YOUTUBE_API_KEY=key
YOUTUBE_CHANNEL_ID=UCxxxxx
TIKTOK_CLIENT_KEY=key
TIKTOK_CLIENT_SECRET=secret
META_ACCESS_TOKEN=token
TWITTER_BEARER_TOKEN=token
```

---

## File Structure Quick Reference

```
creator-ai/
├── main.py                 # Entry point (run this!)
├── requirements.txt        # All dependencies
├── .env                    # Your configuration (create from .env.example)
├── Dockerfile             # Container image
├── docker-compose.yml     # Local dev environment
│
├── src/
│   ├── config.py          # Settings management
│   ├── models/
│   │   └── schemas.py     # Data models (Edit to change data structure)
│   ├── services/
│   │   ├── database.py    # Database operations
│   │   ├── storage.py     # S3 file uploading
│   │   ├── ai_models.py   # LLM/Image generation (Edit prompts here)
│   │   └── platforms.py   # Platform integrations (Add new platforms here)
│   ├── agents/
│   │   ├── content_generator.py  # Content creation agents
│   │   └── distribution.py       # Distribution  agents
│   └── workflows/
│       └── orchestrator.py       # Main workflow coordinator
│
├── docs/
│   ├── SETUP.md          # Installation guide
│   ├── DEPLOYMENT.md     # Cloud deployment
│   ├── CONTENT_STRATEGY.md # Hook formulas & strategies
│   └── EXECUTION_BLUEPRINT.md # Day-by-day execution plan
│
├── .github/
│   └── workflows/
│       └── weekly-content.yml  # GitHub Actions automation
│
└── tests/                # (You can add test files here)
```

---

## Common Edits & Customizations

### Add a New Platform Integration

**File:** `src/services/platforms.py`

```python
class YourPlatformService(PlatformService):
    async def post_content(self, video_url: str, caption: str, **kwargs):
        # Implement posting logic
        pass

    async def get_metrics(self, external_id: str):
        # Implement metrics retrieval
        pass

# Add to registry:
Platform.YOUR_PLATFORM: YourPlatformService()
```

### Customize AI Prompts

**File:** `src/agents/content_generator.py`

Find the prompt string and modify:

```python
hook_prompt = f"""
Create a compelling hook for a {niche.value} content piece.
[Modify this prompt to change how hooks are generated]
"""
```

### Change Content Generation Parameters

**File:** `src/config.py`

```python
BATCH_SIZE = 10  # How many pieces per batch
VARIANTS_PER_PIECE = 5  # A/B test variants
CONTENT_NICHES = "motivational,ai_trends,entertaining"  # Content types
```

### Modify Posting Schedule

**File:** `.github/workflows/weekly-content.yml`

```yaml
schedule:
  - cron: '0 20 * * 5' # Current: Friday 8 PM UTC
  # Change to any time:
  # - cron: '0 9 * * 1'  = Monday 9 AM UTC
  # - cron: '0 15 * * *' = Every day 3 PM UTC
```

---

## Monitoring & Troubleshooting Commands

### Check System Status

```bash
# Health check
python main.py health

# View logs
tail -f logs/creator-ai-*.log

# Check database connection
psql $DATABASE_URL -c "SELECT NOW();"

# Test Ollama
curl http://localhost:11434/api/tags

# Test S3
aws s3 ls s3://creator-ai-content
```

### Database Operations

```bash
# Access database shell
psql $DATABASE_URL

# View all tables
\dt

# See content pieces
SELECT id, title, status, created_at FROM content_pieces LIMIT 10;

# See performance metrics
SELECT * FROM performance_metrics ORDER BY measured_at DESC LIMIT 20;

# Delete old content
DELETE FROM content_pieces WHERE created_at < NOW() - INTERVAL '30 days';
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Generate content (HTTP API)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"niche": "motivational", "count": 1}'

# View metrics
curl http://localhost:8000/metrics
```

---

## Performance Optimization Tips

### Speed Up Content Generation

```bash
# Parallel batch generation (faster)
python main.py cli --count 10 --parallel

# Use GPU for image generation
TTS_DEVICE=cuda python main.py cli

# Cache AI model responses (disable on first run)
CACHE_RESPONSES=true python main.py cli
```

### Reduce Cloud Costs

```env
# Use public HuggingFace models (free)
IMAGE_GENERATION_API=huggingface

# Limit video quality for cheaper storage
VIDEO_QUALITY=720p

# Compress before uploading
COMPRESS_BEFORE_UPLOAD=true
```

### Monitor Resource Usage

```bash
# CPU/Memory while running
top -p $(pgrep -f "python main.py")

# Disk usage
du -sh .

# Database size
SELECT pg_size_pretty(pg_database_size(current_database()));
```

---

## Git Operations

### Commit & Push Changes

```bash
# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Update prompt templates and add new niche"

# Push to GitHub
git push origin main

# Create a backup branch
git branch backup-$(date +%Y%m%d)
```

### Revert Changes

```bash
# Undo last commit (keep files)
git reset --soft HEAD~1

# Discard local changes
git checkout -- src/

# Revert to specific commit
git revert COMMIT_HASH
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] tested locally: `python main.py health`
- [ ] All tests passing: `pytest tests/`
- [ ] Code formatted: `black src/`
- [ ] No lint errors: `flake8 src/`
- [ ] All secrets in GitHub (not in code!)
- [ ] `.env` file is in `.gitignore`
- [ ] Database migrations run
- [ ] API endpoints tested
- [ ] Logs are being captured

---

## Help & Resources

### Official Links

- Docs: `docs/` folder
- GitHub: github.com/morgan9hips-sketch/creator-ai
- Issues: github.com/morgan9hips-sketch/creator-ai/issues

### Configuration Examples

- Prompts: `src/agents/content_generator.py`
- Database: `src/services/database.py`
- APIs: `src/services/platforms.py`

### Learning Resources

- Agent Framework: https://github.com/microsoft/agent-framework
- HuggingFace: https://huggingface.co/docs
- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs

---

## One-Liner Recipes

```bash
# Reset everything to fresh state
rm -rf logs/ && python main.py health

# Generate and immediately post to all platforms
python main.py cli --count 1 --platforms all --auto-post

# Export all content as JSON for backup
sqlite3 creator.db ".mode json" ".output backup.json" "SELECT * FROM content_pieces;"

# Scale to 10 pieces per batch
sed -i 's/BATCH_SIZE = .*/BATCH_SIZE = 10/' src/config.py && python main.py cli

# Run scheduled task immediately (don't wait for cron)
python main.py cli --force-now

# Send all content to specific platform only
python main.py cli --platforms tiktok --auto-post
```

---

**Quick Tip:** Bookmark this page and refer to it often! 🚀
