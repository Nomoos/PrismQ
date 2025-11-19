# Database Decision Tree for Task Queue

**Quick Visual Guide**: Which database should you use for the PrismQ task queue?

```
START: Need a task queue for PrismQ
│
├─❓ Queue on remote server/cloud needed?
│  ├─ YES → ⚠️ Consider cloud DB (AWS RDS, Neon)
│  │         BUT: High latency (10-100ms+), internet dependency
│  │         COST: $200-1200/year after free tier
│  └─ NO  → Continue ↓
│
├─❓ Multi-host deployment required?
│  ├─ YES → ✅ PostgreSQL (with replication) OR cloud DB
│  └─ NO  → Continue ↓
│
├─❓ Throughput > 5,000 tasks/min needed?
│  ├─ YES → ✅ Redis (in-memory, extreme speed)
│  └─ NO  → Continue ↓
│
├─❓ Throughput > 2,000 tasks/min needed?
│  ├─ YES → ✅ PostgreSQL (multi-writer)
│  └─ NO  → Continue ↓
│
├─❓ Sub-millisecond latency required?
│  ├─ YES → ✅ Redis (in-memory)
│  └─ NO  → Continue ↓
│
├─❓ Already have MySQL/PostgreSQL infrastructure?
│  ├─ YES → ✅ Use existing (save setup time)
│  └─ NO  → Continue ↓
│
├─❓ Prefer cloud-managed over local?
│  ├─ YES → ⚠️ Reconsider: Latency penalty, cost, internet dependency
│  │         Local SQLite is faster and free
│  └─ NO  → Continue ↓
│
├─❓ Throughput 200-1000 tasks/min acceptable?
│  ├─ NO  → ⚠️ Re-evaluate requirements
│  └─ YES → Continue ↓
│
└─✅ **USE SQLite** ← YOU ARE HERE
   - Single file database
   - Zero infrastructure
   - Perfect for your needs
   - <1ms latency (vs 10-100ms cloud)
   - $0 cost (vs $200-1200/year cloud)
```

---

## Current PrismQ Requirements

| Requirement | Value | SQLite OK? |
|------------|-------|------------|
| **Platform** | Single Windows host | ✅ YES |
| **Expected Load** | 200-500 tasks/min | ✅ YES |
| **Max Load** | ~1000 tasks/min | ✅ YES |
| **Multi-host** | No | ✅ YES |
| **Team Size** | Small | ✅ YES |
| **Complexity Preference** | Simple | ✅ YES |
| **Infrastructure** | Minimal | ✅ YES |

**Result**: ✅ **SQLite is perfect for PrismQ**

---

## When to Switch

### Add Web Hosting (SQLite + Sync Utility)
- ⚠️ **Web monitoring** needed (dashboard, status views)
- ⚠️ **Remote visibility** for team members
- ⚠️ **Read-only web UI** is sufficient
- ⚠️ **30-60 second data lag** acceptable on web

**Recommended: Keep SQLite + Add Sync Utility**
- ✅ Keep SQLite on Windows (all benefits intact)
- ✅ Sync to web server every 30-60 seconds
- ✅ Web UI for monitoring (read-only)
- ✅ Cost: $60-240/year (web hosting only)
- ✅ Implementation: ~1 week
- ✅ No database migration needed

**Sync Options**: Litestream, rsync, or custom Python script

### Switch to Cloud Database (Neon PostgreSQL) when:
- ⚠️ **Web users need write access** (enqueue tasks from web)
- ⚠️ **Real-time updates** required (<1 second lag)
- ⚠️ **Multi-region** deployment needed
- ⚠️ **Remote workers/teams** need direct access
- ⚠️ Building **SaaS** or web application

**Recommended: Neon PostgreSQL (Serverless)**
- ✅ Free tier always available (300 compute hours/month, 3GB storage)
- ✅ Serverless (auto-scales, scales to zero)
- ✅ PostgreSQL features (`SKIP LOCKED`)
- ✅ Easy migration from SQLite (~2-4 days)
- ✅ Cost: $0-600/year

**Alternative: AWS RDS PostgreSQL** (if using AWS, need 24/7, enterprise compliance)
- ✅ No cold starts, guaranteed uptime
- ✅ Deep AWS integration
- ❌ More expensive: $180-360/year minimum

**Migration Effort**: ~2-4 days (schema, data migration, testing)

**Decision**: Try SQLite + Sync first, only migrate if web write access needed

### Switch to PostgreSQL (Self-Hosted) when:
- ⚠️ **Throughput** consistently exceeds 800-1000 tasks/min
- ⚠️ **SQLITE_BUSY** errors exceed 5% of operations
- ⚠️ **Multi-host** deployment becomes necessary
- ⚠️ Need **distributed** queue across servers

**Migration Effort**: ~1-2 days (schema is compatible)

### Switch to Redis when:
- ⚠️ **Throughput** exceeds 5,000+ tasks/min
- ⚠️ Need **sub-millisecond** latency
- ⚠️ Willing to trade **ACID** for extreme speed
- ⚠️ Have **expertise** in Redis operations

**Migration Effort**: ~3-5 days (different data model)

### Switch to MySQL when:
- ⚠️ Already have **MySQL infrastructure**
- ⚠️ Team has **MySQL expertise** (not PostgreSQL)
- ⚠️ Need MySQL-specific **features** (rare)

**Migration Effort**: ~1-2 days (similar to PostgreSQL)

---

## Decision Summary

```
┌─────────────────────────────────────────────────┐
│  QUESTION: SQLite or MySQL or Other Database?   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  ANSWER: SQLite                                 │
│                                                 │
│  ✅ Zero infrastructure                         │
│  ✅ Single file (C:\Data\queue\queue.db)       │
│  ✅ Perfect for 200-500 tasks/min               │
│  ✅ Easy backup (copy file)                     │
│  ✅ SQL queryable for debugging                 │
│  ✅ Matches "simple architecture" principle     │
│  ✅ Easy upgrade path to PostgreSQL             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  WHY NOT ALTERNATIVES?                          │
│                                                 │
│  MySQL/PostgreSQL:                              │
│    ❌ Requires separate server (overhead)       │
│    ❌ 150-500MB RAM just for server             │
│    ❌ Complex setup (auth, ports, networking)   │
│    ❌ Over-engineering for single host          │
│                                                 │
│  Redis:                                         │
│    ❌ In-memory (data loss risk)                │
│    ❌ No SQL (limited observability)            │
│    ❌ Speed overkill (need 500/min not 50k/min) │
│    ❌ Less robust ACID guarantees               │
└─────────────────────────────────────────────────┘
```

---

## Quick Comparison

| Database | Best For | PrismQ Fit |
|----------|---------|------------|
| **SQLite** | Single host, simple, 100-1k tasks/min | ✅✅✅ **PERFECT** |
| **MySQL** | Multi-host, 5k-10k tasks/min, existing infra | ❌ Over-engineering |
| **PostgreSQL** | Multi-host, 5k-15k tasks/min, scale-up path | ⚠️ Future option |
| **Redis** | Extreme throughput (50k+ tasks/min), caching | ❌ Wrong use case |

---

## Implementation Path

```
Phase 1: SQLite (Current)
├─ Implement with WAL mode
├─ Add monitoring (throughput, SQLITE_BUSY rate)
├─ Document migration path
└─ Use for 6-12+ months

Phase 2: Monitor & Optimize (Months 1-6)
├─ Track performance metrics
├─ Tune PRAGMAs if needed
├─ Optimize queries and indexes
└─ Decide if migration needed

Phase 3: Scale (if needed)
├─ If throughput > 800/min consistently
├─ OR multi-host deployment required
├─ THEN migrate to PostgreSQL
└─ ELSE continue with SQLite
```

---

## Resources

- **[Full Comparison](./DATABASE-COMPARISON-SQLITE-VS-ALTERNATIVES.md)** - Detailed analysis
- **[FAQ](./FAQ-DATABASE-CHOICE.md)** - Common questions
- **[Technical Analysis](./320-sqlite-queue-analysis-and-design.md)** - Deep dive
- **[Implementation Guide](./QUEUE-SYSTEM-QUICK-REFERENCE.md)** - How to implement

---

**Status**: ✅ Decision Made  
**Recommendation**: Use SQLite  
**Review Date**: After 3 months of production use
