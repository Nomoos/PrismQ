# YouTube Video Worker - Quick Deployment Guide

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2025-11-13

---

## Overview

This guide will help you deploy the YouTube Video Worker for production use. The worker processes YouTube video scraping tasks from the TaskManager API and stores results in the IdeaInspiration database.

**Time to Deploy**: ~10 minutes

---

## Prerequisites

- Python 3.10+ installed
- YouTube Data API v3 key
- TaskManager API access (URL + API key)
- Windows, Linux, or macOS system

---

## Quick Start (5 Steps)

### 1. Install Dependencies

```bash
cd Source/Video/YouTube/Video
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy production template
cp .env.production.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Required values to set:**
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your_taskmanager_api_key_here
DATABASE_PATH=data/ideas.db
```

### 3. Initialize Production Environment

```bash
python scripts/init_production.py --register-tasks
```

Expected output:
```
✅ Production initialization complete!
```

### 4. Start Worker

```bash
python scripts/run_worker.py
```

Expected output:
```
================================================================================
YouTube Video Worker Started
================================================================================
Worker ID: youtube-worker-{hostname}-{uuid}
Task Type: youtube_video_single
Poll Interval: 5 seconds
...
```

### 5. Verify Operation

In another terminal:
```bash
# Check worker log
tail -f youtube_worker.log

# Should see task polling messages
```

**Done!** Your worker is now running and processing tasks.

---

## Production Deployment

### Single Worker Deployment

For small-scale deployments (< 100 videos/hour):

```bash
# Start worker in background
nohup python scripts/run_worker.py > logs/worker.log 2>&1 &

# Verify it's running
ps aux | grep run_worker.py

# Check logs
tail -f logs/worker.log
```

### Multi-Worker Deployment

For high-throughput deployments (500+ videos/hour):

```bash
# Start 5 workers
for i in {1..5}; do
    python scripts/run_worker.py \
        --worker-id youtube-worker-$(printf "%03d" $i) \
        > logs/worker_$(printf "%03d" $i).log 2>&1 &
done

# Verify all are running
ps aux | grep run_worker.py | wc -l  # Should show 5

# Monitor workers
tail -f logs/worker_001.log
```

### Systemd Service (Linux)

For production Linux servers, use systemd:

```bash
# Create service file
sudo nano /etc/systemd/system/youtube-worker@.service
```

```ini
[Unit]
Description=YouTube Video Worker %i
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Source/Video/YouTube/Video
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python scripts/run_worker.py --worker-id youtube-worker-%i
Restart=always
RestartSec=10
StandardOutput=append:/var/log/youtube-worker-%i.log
StandardError=append:/var/log/youtube-worker-%i.log

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable youtube-worker@001.service
sudo systemctl start youtube-worker@001.service

# Check status
sudo systemctl status youtube-worker@001.service
```

### Windows Service

For Windows deployment, use NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM: https://nssm.cc/download

# Install as service
nssm install YouTubeWorker "C:\Python310\python.exe" "scripts\run_worker.py"
nssm set YouTubeWorker AppDirectory "C:\Path\To\Source\Video\YouTube\Video"
nssm set YouTubeWorker AppStdout "logs\worker.log"
nssm set YouTubeWorker AppStderr "logs\worker-error.log"

# Start service
nssm start YouTubeWorker

# Check status
nssm status YouTubeWorker
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check if worker is running
ps aux | grep run_worker.py

# Check recent activity
tail -f youtube_worker.log | grep "Task claimed"

# Check for errors
tail -f youtube_worker.log | grep ERROR
```

### Performance Metrics

Monitor in logs:
- Tasks claimed per minute
- Processing time per task
- Success/failure rate
- YouTube API quota usage

### Troubleshooting

**Worker not starting:**
```bash
# Check dependencies
pip install -r requirements.txt

# Check configuration
python scripts/init_production.py

# Check logs
tail -n 100 youtube_worker.log
```

**No tasks being claimed:**
```bash
# Verify TaskManager connection
curl -H "Authorization: Bearer $TASKMANAGER_API_KEY" \
     $TASKMANAGER_API_URL/tasks

# Verify task types registered
python scripts/register_task_types.py

# Check worker logs for connection errors
grep "TaskManager" youtube_worker.log
```

**YouTube API quota exceeded:**
```bash
# Check quota usage
grep "quota" youtube_worker.log

# View quota tracking
cat data/youtube_quota.json

# Wait for quota reset (midnight Pacific Time)
# Or add more API keys with rotation
```

---

## Scaling

### Horizontal Scaling

Add more workers for higher throughput:

```bash
# Scale to 10 workers
for i in {1..10}; do
    python scripts/run_worker.py \
        --worker-id youtube-worker-$(printf "%03d" $i) \
        > logs/worker_$(printf "%03d" $i).log 2>&1 &
done
```

**Considerations:**
- Each worker uses ~50-100 MB RAM
- YouTube API quota is shared across all workers
- More workers = higher throughput but more API usage

### Vertical Scaling

Optimize single worker performance:

```bash
# Increase poll frequency (more responsive)
python scripts/run_worker.py --poll-interval 2

# Decrease poll frequency (less API calls)
python scripts/run_worker.py --poll-interval 10
```

---

## Security Best Practices

1. **Protect API Keys**
   - Never commit `.env` to version control
   - Use environment-specific files
   - Rotate keys regularly

2. **Database Security**
   - Use PostgreSQL for production (instead of SQLite)
   - Enable authentication
   - Regular backups

3. **Network Security**
   - Use HTTPS for TaskManager API
   - Firewall rules for API access
   - VPN for worker-API communication

4. **Access Control**
   - Limit worker permissions
   - Separate service accounts
   - Audit logs regularly

---

## Backup & Recovery

### Database Backup

```bash
# Backup IdeaInspiration database
cp data/ideas.db backups/ideas_$(date +%Y%m%d_%H%M%S).db

# Or use proper SQLite backup
sqlite3 data/ideas.db ".backup backups/ideas_$(date +%Y%m%d_%H%M%S).db"
```

### Configuration Backup

```bash
# Backup configuration
cp .env backups/.env.$(date +%Y%m%d_%H%M%S)

# Backup scripts
tar -czf backups/scripts_$(date +%Y%m%d_%H%M%S).tar.gz scripts/
```

### Recovery

```bash
# Restore database
cp backups/ideas_20250113_120000.db data/ideas.db

# Restore configuration
cp backups/.env.20250113_120000 .env

# Restart workers
killall python  # Stop all workers
python scripts/run_worker.py  # Restart
```

---

## Performance Tuning

### YouTube API Optimization

```bash
# Use batch operations when possible
# Prefer youtube_video_search over multiple youtube_video_single

# Monitor quota usage
tail -f data/youtube_quota.json

# Implement rate limiting
# Set POLL_INTERVAL higher to reduce API calls
```

### Database Optimization

```sql
-- SQLite optimization
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-64000;  -- 64MB cache
PRAGMA temp_store=MEMORY;

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_ideas_source_id ON ideas(source, source_id);
CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON ideas(created_at);
```

### Worker Optimization

```python
# Custom worker configuration
# Adjust based on your needs

# High throughput
POLL_INTERVAL=2
MAX_ITERATIONS=0
HEARTBEAT_INTERVAL=60

# Conservative (low API usage)
POLL_INTERVAL=30
MAX_ITERATIONS=100
HEARTBEAT_INTERVAL=120
```

---

## Next Steps

After successful deployment:

1. **Monitor Performance**
   - Set up alerts for failures
   - Track quota usage
   - Monitor task throughput

2. **Optimize Configuration**
   - Adjust poll interval based on load
   - Scale workers as needed
   - Tune database settings

3. **Integrate with Pipeline**
   - Connect to Classification module
   - Feed to Scoring module
   - Export to downstream systems

4. **Documentation**
   - Document your configuration
   - Create runbooks for common issues
   - Train team on operations

---

## Related Documentation

- **Main README**: `README.md`
- **Scripts Guide**: `scripts/README.md`
- **Worker Guide**: `_meta/docs/YOUTUBE_VIDEO_WORKER.md`
- **Configuration**: `.env.production.example`
- **Next Steps**: `_meta/docs/NEXT-STEPS.md`

---

## Support

**Issues**: See `_meta/docs/TROUBLESHOOTING.md`  
**Architecture**: See `_meta/docs/ARCHITECTURE.md`  
**Contributing**: See `_meta/docs/CONTRIBUTING.md`

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Deployment Time**: ~10 minutes  
**Difficulty**: Easy 🟢
