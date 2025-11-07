# FAQ: Database Choice for PrismQ Task Queue

**Quick Answer**: Use **SQLite 3 with WAL mode**

---

## Common Questions

### Q1: "Why not MySQL? It's more powerful!"

**A:** MySQL is over-engineering for this use case:
- ❌ Requires separate server process (complexity)
- ❌ Uses 200-500MB RAM just for server (overhead)
- ❌ Need to manage authentication, ports, networking
- ❌ More complex backup and deployment
- ✅ SQLite handles our 200-500 tasks/min workload perfectly
- ✅ SQLite is zero infrastructure (single file)

**MySQL is great for**: Multi-host systems, 5k+ tasks/min, when you already have MySQL

### Q2: "Why not PostgreSQL? It has SKIP LOCKED!"

**A:** PostgreSQL is excellent but unnecessary for now:
- ❌ Requires separate server process
- ❌ Uses 150-400MB RAM baseline
- ❌ More complex setup on Windows
- ✅ SQLite works fine with lease-based claiming
- ✅ Can migrate to PostgreSQL later when needed
- ✅ PostgreSQL is our planned upgrade path

**PostgreSQL is great for**: 2k+ tasks/min, multi-host, when scaling beyond SQLite

### Q3: "Why not Redis? It's super fast!"

**A:** Redis is designed for different use cases:
- ❌ In-memory first (data lost on crash unless configured)
- ❌ No SQL (harder to query and debug)
- ❌ Limited ACID guarantees
- ❌ Speed not needed (we need 200-500/min, not 50k+/min)
- ✅ SQLite provides better persistence guarantees
- ✅ SQLite is queryable with SQL

**Redis is great for**: Extreme throughput (10k+ tasks/min), caching, pub/sub

### Q4: "What if SQLite becomes a bottleneck?"

**A:** We have a clear upgrade path:
1. **Monitor**: Track throughput and SQLITE_BUSY errors
2. **Optimize**: Tune PRAGMAs, batching, connection pooling
3. **Decide**: If throughput consistently exceeds 800-1000 tasks/min
4. **Migrate**: Export to PostgreSQL (schema is compatible)

**Timeline**: Expect SQLite to handle needs for 6-12+ months

### Q5: "Can SQLite handle concurrent workers?"

**A:** Yes, with proper configuration:
- ✅ WAL mode enables concurrent readers
- ✅ 4-8 concurrent workers recommended
- ✅ Atomic claiming prevents duplicate processing
- ⚠️ Single writer (one transaction at a time)
- ⚠️ May see SQLITE_BUSY <2% of time (acceptable)

**Key**: Use `PRAGMA busy_timeout=5000` and `isolation_level='IMMEDIATE'`

### Q6: "How do I backup the SQLite database?"

**A:** Extremely simple:
```python
# Option 1: Copy the file (while server is stopped)
copy C:\Data\PrismQ\queue\queue.db C:\Backup\queue-backup.db

# Option 2: Online backup (while server is running)
import sqlite3
conn = sqlite3.connect("queue.db")
backup = sqlite3.connect("backup.db")
conn.backup(backup)
```

**MySQL/PostgreSQL**: Require mysqldump/pg_dump utilities

### Q7: "What about data loss if server crashes?"

**A:** SQLite with WAL mode is very safe:
- ✅ WAL (Write-Ahead Logging) ensures durability
- ✅ Transactions are atomic (all-or-nothing)
- ✅ Database file is crash-resistant
- ✅ Same guarantees as MySQL/PostgreSQL on disk

**Configure**: `PRAGMA synchronous=NORMAL` for balance (vs FULL)

### Q8: "Can I inspect the queue easily?"

**A:** Yes, SQL makes it trivial:
```sql
-- Check queue depth
SELECT status, COUNT(*) FROM task_queue GROUP BY status;

-- View pending tasks
SELECT * FROM task_queue WHERE status='pending' ORDER BY priority;

-- Check worker status
SELECT * FROM workers WHERE last_heartbeat_utc > datetime('now', '-1 minute');
```

Use any SQLite viewer: DB Browser, sqlite3 CLI, or Python

### Q9: "What's the performance difference?"

**A:** For this workload, minimal:
- **SQLite**: 5-10ms enqueue, 10-20ms claim, 500 tasks/min
- **MySQL**: 2-5ms enqueue, 5-10ms claim, 5k tasks/min
- **PostgreSQL**: 2-5ms enqueue, 3-8ms claim, 5k tasks/min
- **Redis**: <1ms enqueue, <1ms claim, 50k tasks/min

**Our needs**: 200-500 tasks/min → SQLite is perfect

### Q10: "What about cloud databases like AWS RDS or Neon? They have free tiers!"

**A:** Cloud databases don't make sense for this use case:
- ❌ **Latency**: 10-100ms+ (internet) vs <1ms (local SQLite)
- ❌ **Internet Dependency**: Requires stable connection, works offline with SQLite
- ❌ **Cost**: Free tiers have limits, then $200-1200/year vs $0 forever
- ❌ **Complexity**: AWS accounts, VPCs, credentials vs zero config
- ❌ **Data Privacy**: Data in cloud vs 100% local
- ✅ **SQLite**: Perfect for single Windows host task queue

**Cloud databases solve problems we don't have** (multi-host, remote access) while **introducing problems we can't accept** (latency, internet dependency).

**Cloud is great for**: Web apps, multi-region deployments, remote teams  
**Cloud is NOT for**: Local Windows task queues with GPU workers

See [DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md](./DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md) for detailed cloud pricing and comparison.

### Q11: "If we need web hosting in the future, should we migrate to cloud database?"

**A: No - use SQLite + Sync Utility instead** (unless web users need write access)

**Recommended Approach: SQLite + Sync**
- ✅ **Keep SQLite** on Windows host (all benefits intact)
- ✅ **Add sync utility** (Litestream, rsync, or custom script)
- ✅ **Web UI** connects to synced replica (read-only monitoring)
- ✅ **Cost**: $60-240/year (web hosting only, no DB migration)
- ✅ **Implementation**: ~1 week

**How it works:**
```
Windows Host (SQLite) → Sync Utility → Web Server (SQLite replica)
                         (every 30-60s)
```

**Only migrate to cloud DB (Neon) if:**
- Web users need to enqueue tasks (write access)
- Need <1 second real-time updates on web
- Multi-region write operations required

See [DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md](./DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md) section "SQLite + Sync Utility (Hybrid Architecture)" for detailed guide.

### Q12: "If we need to host online in the future, which cloud database should we use?"

**A: Neon (Serverless PostgreSQL)** - but only if SQLite + Sync won't work

**Why Neon:**
- ✅ **PostgreSQL** (natural migration from SQLite, `SKIP LOCKED` support)
- ✅ **Always-free tier** (300 compute hours/month, 3GB storage)
- ✅ **Serverless** (auto-scales, scales to zero, cost-efficient)
- ✅ **Git-like branching** (great for dev/test environments)
- ✅ **Easy migration** (~2-4 days from SQLite)
- ✅ **Cost**: $0-600/year (vs $180-1200/year for alternatives)

**Alternative: AWS RDS PostgreSQL** if:
- Already using AWS infrastructure
- Need guaranteed 24/7 uptime (no cold starts)
- Enterprise compliance requirements
- Budget allows $180-360/year minimum

**But first consider**: SQLite + Sync Utility ($60-240/year, no migration needed)

### Q13: "What if requirements change?"

**A:** Easy to adapt:
- **Scale up**: Migrate to PostgreSQL (schema mostly compatible)
- **Go cloud**: Migrate to Neon (recommended) or AWS RDS
- **Scale out**: Add Redis for extreme throughput
- **Keep simple**: Stay with SQLite (handles 1000 tasks/min)

**Migration effort**: ~2-4 days to cloud PostgreSQL (schema, data, testing)

---

## Decision Summary

### Local Databases

| Criteria | SQLite | MySQL | PostgreSQL | Redis |
|----------|--------|-------|------------|-------|
| **Our Use Case** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐ Overkill | ⭐⭐⭐ Future | ⭐⭐ Wrong fit |
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Windows** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ Sufficient | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Extreme |
| **Upgrade Path** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### Cloud Databases

| Criteria | AWS RDS | Neon | PlanetScale | Supabase |
|----------|---------|------|-------------|----------|
| **Our Use Case** | ⭐ Wrong fit | ⭐ Wrong fit | ⭐ Wrong fit | ⭐ Wrong fit |
| **Latency** | ⭐⭐ 10-100ms+ | ⭐⭐ 10-100ms+ | ⭐⭐ 10-100ms+ | ⭐⭐ 10-100ms+ |
| **Cost** | ⭐⭐⭐ $180-360/yr | ⭐⭐ $600-1200/yr | ⭐⭐ $468/yr | ⭐⭐⭐ $300/yr |
| **Complexity** | ⭐⭐ AWS setup | ⭐⭐⭐ Account only | ⭐⭐⭐ Account only | ⭐⭐⭐ Account only |
| **Offline Use** | ❌ No | ❌ No | ❌ No | ❌ No |

**Winner: SQLite** ✅ (Local, fast, free, simple)

---

## Quick Start (SQLite)

```python
import sqlite3

# Connect with proper configuration
conn = sqlite3.connect("queue.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")

# Create schema
conn.execute("""
    CREATE TABLE IF NOT EXISTS task_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        priority INTEGER DEFAULT 5,
        created_at_utc TEXT NOT NULL,
        claimed_by TEXT,
        claimed_at_utc TEXT
    )
""")

# Enqueue task (default isolation is fine)
conn.execute("""
    INSERT INTO task_queue (type, priority, created_at_utc)
    VALUES (?, ?, datetime('now'))
""", ("youtube_download", 3))
conn.commit()

# Claim task (use IMMEDIATE transaction for atomic claiming)
conn.isolation_level = None  # Autocommit mode
conn.execute("BEGIN IMMEDIATE")  # Start IMMEDIATE transaction
try:
    cursor = conn.execute("""
        UPDATE task_queue 
        SET status='claimed', claimed_by=?, claimed_at_utc=datetime('now')
        WHERE rowid = (
            SELECT rowid FROM task_queue
            WHERE status='pending'
            ORDER BY priority ASC, id ASC
            LIMIT 1
        )
        RETURNING *
    """, ("worker-01",))
    task = cursor.fetchone()
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

---

## When to Reconsider

**Upgrade to PostgreSQL if:**
- ⚠️ Throughput consistently exceeds 800-1000 tasks/min
- ⚠️ SQLITE_BUSY errors exceed 5%
- ⚠️ Need multi-host deployment

**Upgrade to MySQL if:**
- ⚠️ Already have MySQL infrastructure
- ⚠️ Team has MySQL expertise
- ⚠️ Need MySQL-specific features

**Upgrade to Redis if:**
- ⚠️ Throughput exceeds 10k+ tasks/min
- ⚠️ Need sub-millisecond latency
- ⚠️ Willing to trade ACID for speed

---

## Full Documentation

For complete analysis, see:
- **[Database Comparison](./DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md)** - Comprehensive comparison
- **[#320: Analysis](./320-sqlite-queue-analysis-and-design.md)** - Technical analysis
- **[Queue System README](../THE-QUEUE-README.md)** - Implementation overview

---

**Status**: ✅ Recommended  
**Last Updated**: 2025-11-05  
**Next Review**: After 3 months of production use
