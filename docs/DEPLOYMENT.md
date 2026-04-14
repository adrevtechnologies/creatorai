# Deployment Guide - Cloud Hosting (Free Tier)

Deploy Creator-AI to the cloud with **zero monthly cost** using free tier services.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CREATOR-AI CLOUD STACK                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend/API Layer                                           │
│  └─ Railway.app (Python backend) - $5/month (free tier)    │
│                                                               │
│  Data Layer                                                   │
│  └─ Supabase PostgreSQL - Free (500MB)                      │
│                                                               │
│  Storage Layer                                                │
│  └─ AWS S3 - Free tier (5GB/12mo)                          │
│                                                               │
│  AI Models                                                    │
│  └─ HuggingFace Spaces - Free (public)                      │
│                                                               │
│ Automation                                                    │
│  └─ GitHub Actions - Free (2000 min/month)                 │
│                                                               │
│  Monitoring (Optional)                                        │
│  └─ Sentry - Free (5000 events/month)                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Deployment

### Phase 1: Prepare Cloud Services

#### 1.1 Supabase Database Setup

1. Sign up at https://supabase.com
2. Create new project
3. Note: `Project URL` and `API Key` (anon key)
4. Use these in your `.env`:
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   ```

#### 1.2 AWS S3 Setup

1. Create AWS account (free tier eligible)
2. Go to S3 console
3. Create bucket: `creator-ai-content`
4. Create IAM user with S3 permissions
5. Generate access keys
6. Add to `.env`:
   ```env
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   S3_BUCKET_NAME=creator-ai-content
   ```

#### 1.3 Git Repository

```bash
# Make sure you've committed everything
git add .
git commit -m "Initial Creator-AI deployment"
git push origin main
```

### Phase 2: Deploy to Railway

Railway is the easiest free-tier option for Python apps.

#### 2.1 Railway Setup

1. Go to https://railway.app/dashboard
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `creator-ai` repository
6. Wait for deployment (may take 2-3 minutes)

#### 2.2 Configure Environment Variables

In Railway dashboard:

1. Go to project settings
2. Click "Variables" tab
3. Add all environment variables from `.env`
4. **Important:** Use your real credentials (not mock values)
5. Save and redeploy

#### 2.3 Set Up Services

In Railway, click "Services" and use environment variables to connect:

1. **Database Service** (Supabase)
   - No setup needed - Railway connects via connection string
2. **Storage Service** (AWS S3)
   - Configured via `AWS_` environment variables

3. **AI Models** (HuggingFace)
   - Configured via `HUGGINGFACE_API_KEY`

#### 2.4 Verify Deployment

```bash
# Get Railway service URL from dashboard
curl https://your-app.up.railway.app/health

# Should return:
# {"status": "healthy", "environment": "production"}
```

### Phase 3: GitHub Actions Scheduling

Automate content generation with **free** GitHub Actions.

#### 3.1 Add Secrets to GitHub

1. Go to repository Settings
2. Secrets and variables → Actions
3. Add Repository Secrets (same as your `.env`):

```
SUPABASE_URL
SUPABASE_KEY
HUGGINGFACE_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
YOUTUBE_API_KEY
YOUTUBE_CHANNEL_ID
TIKTOK_CLIENT_KEY
TIKTOK_CLIENT_SECRET
TIKTOK_ACCESS_TOKEN
META_APP_ID
META_APP_SECRET
META_ACCESS_TOKEN
TWITTER_BEARER_TOKEN
LINKEDIN_ACCESS_TOKEN
RAILWAY_TOKEN (from Railway dashboard)
RAILWAY_SERVICE_ID (from Railway dashboard)
```

#### 3.2 GitHub Actions Already Configured

The workflow `.github/workflows/weekly-content.yml` is already set up to:

- Generate content every Friday at 8 PM UTC
- Deploy to Railway if successful
- Send notifications on success/failure

To modify schedule, edit the workflow and change the cron expression:

```yaml
schedule:
  - cron: '0 20 * * 5' # Format: minute hour day-of-month month day-of-week
```

### Phase 4: Monitoring & Maintenance

#### 4.1 View Logs

Railway dashboard shows real-time logs. Also available via CLI:

```bash
npm install -g @railway/cli
railway login
railway logs --service creator-ai-app
```

#### 4.2 Database Backups

Supabase automatically backs up daily. To manually export:

```bash
# Via CLI
psql $DATABASE_URL -c "\\dt"

# Or download from Supabase dashboard
```

#### 4.3 Monitor Costs

- **Railway:** Free tier (~$5/month if you exceed free tier)
- **Supabase:** Free tier (500MB storage)
- **S3:** Free tier (5GB/month for 12 months)
- **GitHub Actions:** Free tier (2000 minutes/month)
- **Total:** ~$0-5/month

## Scaling Beyond Free Tier

As you grow, you can add:

| Service        | Free Tier   | Paid Tier    | Use Case       |
| -------------- | ----------- | ------------ | -------------- |
| Railway        | ~$5/mo      | $0.50/CPU-hr | App hosting    |
| Supabase       | 500MB       | $25+/mo      | Database       |
| AWS S3         | 5GB/12mo    | $0.023/GB    | Storage        |
| GitHub Actions | 2000 min/mo | $0.008/min   | Automation     |
| Sentry         | 5000 events | $29+/mo      | Error tracking |

## Troubleshooting Deployment

### App crashes on startup

1. Check Railway logs
2. Verify all environment variables are set
3. Test locally: `python main.py health`

### Database connection errors

```bash
# Test connection
psql $DATABASE_URL

# If fails, check:
# - Supabase is running
# - Firewall allows connection
# - Connection string is correct
```

### S3 upload fails

```bash
# Test S3 permissions
aws s3 ls s3://creator-ai-content --profile default

# If fails:
# - Verify IAM user has S3 permissions
# - Check bucket exists
# - Verify access keys
```

### GitHub Actions not triggering

1. Check workflow is enabled: `.github/workflows/weekly-content.yml`
2. Verify cron syntax: https://crontab.guru/
3. Check Actions tab for logs
4. Manual trigger: `workflow_dispatch`

## Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations run successfully
- [ ] S3 bucket created and accessible
- [ ] Platform APIs configured and tested
- [ ] GitHub Actions secrets added
- [ ] Workflow schedule verified
- [ ] Health check passing
- [ ] Logs accessible and clean
- [ ] Backup strategy confirmed
- [ ] Cost monitoring set up

## Disaster Recovery

### Backup Strategy

```bash
# Export database weekly
pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp backup-*.sql.gz s3://creator-ai-backups/
```

### Restore Procedure

```bash
# If database is corrupted:
gzip -d backup-20240101.sql.gz
psql $DATABASE_URL < backup-20240101.sql
```

### Point-in-time Recovery

Supabase keeps backups for 7 days. Contact support for restoration.

## Next Steps

1. **Monitor first week:** Check logs daily
2. **Analyze content performance:** Use analytics dashboard
3. **Optimize based on metrics:** Adjust strategies weekly
4. **Scale horizontally:** Add more content niches
5. **Expand to paid services:** As budget allows

## Support

- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs
- AWS Docs: https://docs.aws.amazon.com
- GitHub Actions: https://docs.github.com/en/actions
