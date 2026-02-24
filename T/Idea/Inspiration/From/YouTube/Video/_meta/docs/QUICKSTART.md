# YouTube Video Worker - Quick Start Guide

Get started with YouTube Video Worker in 5 minutes!

---

## ⚡ Prerequisites (2 minutes)

1. **Python 3.10+** installed
2. **YouTube API Key** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. **TaskManager API** credentials (for production)

---

## 🚀 Quick Start (3 minutes)

### Step 1: Setup (1 minute)

```bash
cd Source/Video/YouTube/Video

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp .env.production.example .env
```

### Step 2: Configure (1 minute)

Edit `.env` file:

```bash
# Required
YOUTUBE_API_KEY=your_youtube_api_key_here
DATABASE_PATH=data/ideas.db
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your_taskmanager_api_key_here
```

### Step 3: Initialize (30 seconds)

```bash
python scripts/init_production.py --register-tasks
```

Expected output:
```
✅ Production initialization complete!
```

### Step 4: Start Worker (30 seconds)

```bash
python scripts/run_worker.py
```

Expected output:
```
================================================================================
YouTube Video Worker Started
================================================================================
Worker ID: youtube-worker-hostname-12ab34cd
Task Type: youtube_video_single
Poll Interval: 5 seconds
...
```

**That's it!** Your worker is now running and processing tasks.

---

## 🎯 Common Tasks

### Test with Limited Iterations

```bash
python scripts/run_worker.py --max-iterations 10
```

### Run Multiple Workers

```bash
# Terminal 1
python scripts/run_worker.py --worker-id worker-001

# Terminal 2
python scripts/run_worker.py --worker-id worker-002

# Terminal 3
python scripts/run_worker.py --worker-id worker-003
```

### Use Different Task Type

```bash
# For search-based scraping
python scripts/run_worker.py --task-type youtube_video_search

# For general scraping
python scripts/run_worker.py --task-type youtube_video_scrape
```

### Custom Poll Interval

```bash
# More responsive (higher API usage)
python scripts/run_worker.py --poll-interval 2

# More conservative (lower API usage)
python scripts/run_worker.py --poll-interval 30
```

---

## 🔍 Monitoring

### View Logs

```bash
# Real-time log viewing
tail -f youtube_worker.log

# Search for errors
grep ERROR youtube_worker.log

# View last 50 lines
tail -n 50 youtube_worker.log
```

### Check Worker Status

```bash
# See running workers
ps aux | grep run_worker.py

# Count running workers
ps aux | grep run_worker.py | grep -v grep | wc -l
```

### View Database

```bash
# SQLite command line
sqlite3 data/ideas.db

# Count scraped videos
sqlite3 data/ideas.db "SELECT COUNT(*) FROM ideas WHERE source='youtube'"

# View recent videos
sqlite3 data/ideas.db "SELECT title, created_at FROM ideas WHERE source='youtube' ORDER BY created_at DESC LIMIT 10"
```

---

## 🛠️ Troubleshooting

### Problem: Worker not starting

**Solution:**
```bash
# Check dependencies
pip install -r requirements.txt

# Verify configuration
python scripts/init_production.py --skip-validation
```

### Problem: No tasks being claimed

**Solution:**
```bash
# Verify TaskManager connection
echo $TASKMANAGER_API_URL
echo $TASKMANAGER_API_KEY

# Register task types
python scripts/register_task_types.py

# Check logs
tail -f youtube_worker.log | grep "TaskManager"
```

### Problem: YouTube API errors

**Solution:**
```bash
# Verify API key
echo $YOUTUBE_API_KEY

# Check quota usage
cat data/youtube_quota.json

# Test API manually
python -c "
from googleapiclient.discovery import build
import os
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
print('API key is valid!')
"
```

---

## 📚 Next Steps

### Learn More
- **Full Deployment**: See `DEPLOYMENT_GUIDE.md`
- **Worker Guide**: See `_meta/docs/YOUTUBE_VIDEO_WORKER.md`
- **Architecture**: See `README.md`
- **Scripts**: See `scripts/README.md`

### Production Deployment
- Set up systemd service (Linux)
- Set up NSSM service (Windows)
- Configure monitoring and alerts
- Set up database backups

### Optimization
- Tune poll interval
- Scale workers horizontally
- Optimize YouTube API usage
- Monitor performance metrics

---

## 💡 Tips

1. **Start Small**: Begin with 1 worker and limited iterations
2. **Monitor Quota**: Watch YouTube API quota carefully
3. **Use Logs**: Check logs frequently when starting
4. **Scale Gradually**: Add more workers as needed
5. **Test Locally**: Test with local queue before production

---

## 📞 Getting Help

- **Documentation**: `_meta/docs/`
- **Scripts Help**: `python scripts/run_worker.py --help`
- **Examples**: `examples/example_usage.py`
- **Issues**: Check `_meta/docs/TROUBLESHOOTING.md`

---

## ✅ Checklist

Before going to production:

- [ ] Dependencies installed
- [ ] `.env` configured with valid credentials
- [ ] `init_production.py` runs successfully
- [ ] Task types registered
- [ ] Worker starts and claims tasks
- [ ] Results appear in database
- [ ] Logs show no errors
- [ ] Quota monitoring active
- [ ] Backup strategy in place
- [ ] Monitoring configured

---

**Time to Complete**: ~5 minutes  
**Difficulty**: Easy 🟢  
**Status**: ✅ Production Ready

---

Happy scraping! 🎉
