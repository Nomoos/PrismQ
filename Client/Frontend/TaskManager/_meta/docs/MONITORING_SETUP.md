# Monitoring Setup Guide - Frontend/TaskManager

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Owner:** Worker08 - DevOps & Deployment Specialist

## Overview

This guide covers monitoring setup for Frontend/TaskManager in staging and production environments. Effective monitoring enables early issue detection, quick response times, and data-driven improvements.

## Table of Contents

1. [Monitoring Strategy](#monitoring-strategy)
2. [Health Check Monitoring](#health-check-monitoring)
3. [Error Tracking (Sentry)](#error-tracking-sentry)
4. [Performance Monitoring](#performance-monitoring)
5. [Uptime Monitoring](#uptime-monitoring)
6. [Log Monitoring](#log-monitoring)
7. [Alert Configuration](#alert-configuration)
8. [Dashboard Setup](#dashboard-setup)
9. [Incident Response](#incident-response)

## Monitoring Strategy

### Monitoring Tiers

**Tier 1: Critical (Real-time alerts)**
- Application down/unavailable
- Error rate spike (>5% of requests)
- API connectivity failure
- Security incidents
- Performance collapse (>10s load time)

**Tier 2: Important (Alert within 15 min)**
- Performance degradation (>50% slower)
- Elevated error rates (2-5%)
- High memory usage
- Failed deployments
- Mobile-specific issues

**Tier 3: Informational (Daily digest)**
- Minor performance changes
- Low error rates (<2%)
- Usage statistics
- Feature adoption
- User feedback

### Monitoring Principles

1. **Proactive, not reactive** - Detect before users report
2. **Actionable alerts** - Every alert needs clear action
3. **Reduce noise** - Avoid alert fatigue
4. **Context matters** - Provide enough info to debug
5. **User-focused** - Monitor what matters to users

## Health Check Monitoring

### Health Endpoint Setup

The application provides a `/health.json` endpoint for monitoring.

**Health Check Response:**
```json
{
  "status": "ok",
  "service": "PrismQ Frontend/TaskManager",
  "version": "0.1.0",
  "environment": "production",
  "deployed_at": "2025-11-10T12:00:00Z",
  "build": {
    "bundle_size_kb": 210,
    "gzipped_size_kb": 71,
    "build_date": "2025-11-10"
  },
  "checks": {
    "static_files": "ok",
    "spa_routing": "ok"
  }
}
```

### Health Check Monitoring Script

Create a monitoring script:

```bash
#!/bin/bash
# health-monitor.sh - Monitor Frontend/TaskManager health

HEALTH_URL="https://your-domain.com/health.json"
ALERT_EMAIL="alerts@your-domain.com"
LOG_FILE="/var/log/frontend-health.log"

check_health() {
    response=$(curl -s -w "%{http_code}" "$HEALTH_URL")
    http_code="${response: -3}"
    body="${response:0:-3}"
    
    if [ "$http_code" != "200" ]; then
        echo "$(date): ALERT - Health check failed with HTTP $http_code" | tee -a "$LOG_FILE"
        send_alert "Frontend Health Check Failed" "HTTP $http_code"
        return 1
    fi
    
    status=$(echo "$body" | jq -r '.status')
    if [ "$status" != "ok" ]; then
        echo "$(date): ALERT - Health status is $status" | tee -a "$LOG_FILE"
        send_alert "Frontend Health Status" "Status: $status"
        return 1
    fi
    
    echo "$(date): Health check passed" >> "$LOG_FILE"
    return 0
}

send_alert() {
    subject="$1"
    message="$2"
    echo "$message" | mail -s "[ALERT] $subject" "$ALERT_EMAIL"
}

# Run check
check_health
exit $?
```

**Cron Setup:**
```cron
# Check health every 5 minutes
*/5 * * * * /usr/local/bin/health-monitor.sh

# Daily health report
0 9 * * * /usr/local/bin/health-report.sh
```

### External Health Monitoring

**Recommended Services:**
1. **UptimeRobot** (Free tier available)
   - Monitor: `https://your-domain.com/health.json`
   - Interval: 5 minutes
   - Alert: Email/SMS on failure

2. **Pingdom** (Paid)
   - More detailed monitoring
   - Performance tracking
   - Global locations

3. **StatusCake** (Free tier available)
   - Uptime monitoring
   - Page speed monitoring
   - SSL certificate monitoring

**Setup Example (UptimeRobot):**
```yaml
Monitor Type: HTTP(s)
URL: https://your-domain.com/health.json
Alert Contacts: team@your-domain.com
Interval: 5 minutes
Expected Response: "status":"ok"
```

## Error Tracking (Sentry)

### Sentry Integration

Install Sentry for production error tracking.

**1. Install Sentry SDK:**
```bash
npm install @sentry/vue @sentry/vite-plugin
```

**2. Configure Sentry in main.ts:**
```typescript
// src/main.ts
import { createApp } from 'vue'
import * as Sentry from '@sentry/vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Initialize Sentry in production only
if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_APP_ENV || 'production',
    
    // Performance monitoring
    integrations: [
      new Sentry.BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      }),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    
    // Sample rate for performance monitoring
    tracesSampleRate: 1.0,
    
    // Session replay
    replaysSessionSampleRate: 0.1,  // 10% of sessions
    replaysOnErrorSampleRate: 1.0,  // 100% of sessions with errors
    
    // Release tracking
    release: `frontend-taskmanager@${import.meta.env.VITE_APP_VERSION || '0.1.0'}`,
    
    // User context
    beforeSend(event, hint) {
      // Add custom context
      event.tags = {
        ...event.tags,
        worker_id: localStorage.getItem('worker_id') || 'unknown',
      }
      
      // Filter out sensitive data
      if (event.request?.headers) {
        delete event.request.headers['Authorization']
      }
      
      return event
    },
  })
}

app.use(router)
app.mount('#app')
```

**3. Add to vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { sentryVitePlugin } from '@sentry/vite-plugin'

export default defineConfig({
  plugins: [
    vue(),
    
    // Upload source maps to Sentry in production builds
    sentryVitePlugin({
      org: process.env.VITE_SENTRY_ORG,
      project: process.env.VITE_SENTRY_PROJECT,
      authToken: process.env.VITE_SENTRY_AUTH_TOKEN,
      
      // Only upload in production
      disable: process.env.NODE_ENV !== 'production',
      
      // Source maps configuration
      sourcemaps: {
        assets: './dist/assets/**',
      },
    }),
  ],
  
  build: {
    sourcemap: true,  // Enable source maps for debugging
  },
})
```

**4. Environment Configuration:**
```bash
# .env.production
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
VITE_SENTRY_ORG=your-org
VITE_SENTRY_PROJECT=frontend-taskmanager
VITE_SENTRY_AUTH_TOKEN=your-auth-token
VITE_APP_VERSION=0.1.0
```

### Sentry Alert Configuration

**Critical Alerts (Immediate notification):**
```yaml
Alert Name: Critical Errors in Production
Conditions:
  - Error rate > 5% in 5 minutes
  - OR specific error: "API Connection Failed"
  - AND environment = production
Actions:
  - Email: team@your-domain.com
  - Slack: #alerts
  - PagerDuty (if configured)
```

**Performance Alerts:**
```yaml
Alert Name: Performance Degradation
Conditions:
  - Average page load time > 5 seconds
  - OR Time to Interactive > 10 seconds
  - Over 10-minute window
Actions:
  - Email: dev-team@your-domain.com
  - Slack: #performance
```

**Error Spike Detection:**
```yaml
Alert Name: Error Spike
Conditions:
  - Error count increases by 300% compared to previous hour
  - Minimum 10 errors
Actions:
  - Email: on-call@your-domain.com
  - Slack: #incidents
```

### Sentry Dashboard

**Key Metrics to Track:**
1. **Error Rate:** Errors per user session
2. **Unique Errors:** Number of distinct error types
3. **Affected Users:** How many users hit errors
4. **Error Trends:** Increasing or decreasing
5. **Release Comparison:** New vs old version errors

**Custom Dashboard Widgets:**
- Error count by route
- Most common errors
- Errors by browser/device
- Performance metrics by page
- User impact assessment

## Performance Monitoring

### Web Vitals Tracking

Track Core Web Vitals using the `web-vitals` library (already installed).

**1. Create performance tracker:**
```typescript
// src/utils/performance.ts
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

export function initPerformanceTracking() {
  // Only in production
  if (import.meta.env.DEV) return

  function sendToAnalytics(metric: any) {
    // Send to your analytics service
    console.log('Performance metric:', metric)
    
    // Example: Send to custom endpoint
    fetch('/api/analytics/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metric),
    }).catch(err => {
      console.error('Failed to send performance metric:', err)
    })
  }

  // Track Core Web Vitals
  onCLS(sendToAnalytics)  // Cumulative Layout Shift
  onFID(sendToAnalytics)  // First Input Delay
  onLCP(sendToAnalytics)  // Largest Contentful Paint
  onFCP(sendToAnalytics)  // First Contentful Paint
  onTTFB(sendToAnalytics) // Time to First Byte
}
```

**2. Initialize in main.ts:**
```typescript
import { initPerformanceTracking } from './utils/performance'

// After app mount
app.mount('#app')
initPerformanceTracking()
```

### Performance Thresholds

**Target Metrics:**
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1
- **FCP (First Contentful Paint):** < 1.8s
- **TTFB (Time to First Byte):** < 600ms
- **Total Page Load:** < 3s

**Alert on:**
- LCP > 4s
- FID > 300ms
- CLS > 0.25
- Total load > 5s

### Lighthouse CI

Already configured in `lighthouserc.js`. Use for automated performance testing.

**Run Lighthouse:**
```bash
npm run lighthouse
```

**CI Integration:**
```yaml
# .github/workflows/performance.yml
name: Performance Check
on:
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install
        run: npm ci
      - name: Build
        run: npm run build
      - name: Lighthouse CI
        run: npm run lighthouse:ci
```

## Uptime Monitoring

### Server-Side Monitoring

**Apache Access Logs:**
```bash
# Monitor access patterns
tail -f /var/log/apache2/access.log | grep "GET / "

# Count requests per minute
tail -f /var/log/apache2/access.log | awk '{print $4}' | cut -d: -f1-3 | uniq -c

# Monitor for errors
tail -f /var/log/apache2/error.log | grep -i error
```

**Error Rate Calculation:**
```bash
#!/bin/bash
# error-rate.sh - Calculate error rate from logs

LOG_FILE="/var/log/apache2/access.log"
WINDOW_MINUTES=5

# Get total requests in window
total=$(tail -10000 "$LOG_FILE" | wc -l)

# Get 4xx and 5xx errors
errors=$(tail -10000 "$LOG_FILE" | awk '$9 >= 400' | wc -l)

# Calculate error rate
if [ "$total" -gt 0 ]; then
    error_rate=$(echo "scale=2; ($errors / $total) * 100" | bc)
    echo "Error rate: $error_rate% ($errors errors in $total requests)"
    
    # Alert if error rate > 5%
    if (( $(echo "$error_rate > 5" | bc -l) )); then
        echo "ALERT: Error rate exceeds threshold!"
        # Send alert
    fi
else
    echo "No requests in window"
fi
```

### Response Time Monitoring

```bash
#!/bin/bash
# response-time.sh - Monitor response times

URL="https://your-domain.com"
THRESHOLD=3000  # milliseconds

while true; do
    start=$(date +%s%N)
    response=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
    end=$(date +%s%N)
    
    duration=$(( (end - start) / 1000000 ))  # Convert to ms
    
    if [ "$response" != "200" ]; then
        echo "$(date): ALERT - HTTP $response"
    elif [ "$duration" -gt "$THRESHOLD" ]; then
        echo "$(date): ALERT - Slow response: ${duration}ms"
    else
        echo "$(date): OK - ${duration}ms"
    fi
    
    sleep 60
done
```

## Log Monitoring

### Application Logs

**Client-Side Logging:**
```typescript
// src/utils/logger.ts
export class Logger {
  private static instance: Logger
  
  private constructor() {}
  
  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }
  
  log(level: 'info' | 'warn' | 'error', message: string, context?: any) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      url: window.location.href,
      userAgent: navigator.userAgent,
    }
    
    // Console in development
    if (import.meta.env.DEV) {
      console[level](message, context)
    }
    
    // Send to logging service in production
    if (import.meta.env.PROD) {
      this.sendToLoggingService(entry)
    }
  }
  
  private sendToLoggingService(entry: any) {
    // Send to your logging service
    // Examples: Datadog, LogRocket, Loggly, etc.
  }
  
  info(message: string, context?: any) {
    this.log('info', message, context)
  }
  
  warn(message: string, context?: any) {
    this.log('warn', message, context)
  }
  
  error(message: string, context?: any) {
    this.log('error', message, context)
  }
}

export const logger = Logger.getInstance()
```

### Server Logs

**Log Aggregation:**
```bash
# Aggregate logs from multiple servers
# Use rsyslog, Fluentd, or similar

# Example: Send logs to centralized server
# /etc/rsyslog.d/frontend.conf
*.* @@log-server.your-domain.com:514
```

**Log Rotation:**
```bash
# /etc/logrotate.d/frontend
/var/log/frontend/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        service apache2 reload > /dev/null
    endscript
}
```

## Alert Configuration

### Alert Channels

**1. Email Alerts**
```bash
# Configure email alerts
# /etc/ssmtp/ssmtp.conf
root=alerts@your-domain.com
mailhub=smtp.gmail.com:587
AuthUser=your-email@gmail.com
AuthPass=your-password
UseSTARTTLS=YES
```

**2. Slack Alerts**
```bash
#!/bin/bash
# slack-alert.sh
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

send_slack_alert() {
    local message="$1"
    local severity="$2"
    
    payload="{
        \"text\": \"🚨 Frontend Alert\",
        \"attachments\": [{
            \"color\": \"${severity}\",
            \"text\": \"${message}\",
            \"footer\": \"Frontend/TaskManager\",
            \"ts\": $(date +%s)
        }]
    }"
    
    curl -X POST -H 'Content-type: application/json' \
        --data "$payload" "$WEBHOOK_URL"
}

# Usage
send_slack_alert "Health check failed" "danger"
```

**3. SMS Alerts (via Twilio)**
```bash
#!/bin/bash
# sms-alert.sh
ACCOUNT_SID="your-account-sid"
AUTH_TOKEN="your-auth-token"
FROM_NUMBER="+1234567890"
TO_NUMBER="+0987654321"

send_sms_alert() {
    local message="$1"
    
    curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$ACCOUNT_SID/Messages.json" \
        --data-urlencode "From=$FROM_NUMBER" \
        --data-urlencode "To=$TO_NUMBER" \
        --data-urlencode "Body=$message" \
        -u "$ACCOUNT_SID:$AUTH_TOKEN"
}

# Usage
send_sms_alert "CRITICAL: Frontend down!"
```

### Alert Rules

**Critical (Immediate):**
- Application down (health check fails 3 times in a row)
- Error rate > 10%
- Response time > 10 seconds
- All API calls failing

**High (Within 15 min):**
- Error rate 5-10%
- Response time 5-10 seconds
- Performance degradation > 50%
- High memory usage

**Medium (Within 1 hour):**
- Error rate 2-5%
- Response time 3-5 seconds
- Moderate performance issues
- Elevated warning count

**Low (Daily digest):**
- Error rate < 2%
- Minor issues
- Informational metrics
- Usage statistics

## Dashboard Setup

### Monitoring Dashboard

Create a simple monitoring dashboard:

**Example: Simple HTML Dashboard**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Frontend Monitoring Dashboard</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .metric { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .metric.ok { border-left: 5px solid #28a745; }
        .metric.warning { border-left: 5px solid #ffc107; }
        .metric.error { border-left: 5px solid #dc3545; }
        .value { font-size: 32px; font-weight: bold; }
        .label { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <h1>Frontend/TaskManager - Monitoring Dashboard</h1>
    
    <div id="metrics">
        <div class="metric ok">
            <div class="label">Status</div>
            <div class="value" id="status">Checking...</div>
        </div>
        
        <div class="metric ok">
            <div class="label">Response Time</div>
            <div class="value" id="response-time">--</div>
        </div>
        
        <div class="metric ok">
            <div class="label">Error Rate</div>
            <div class="value" id="error-rate">--</div>
        </div>
    </div>
    
    <script>
        async function updateMetrics() {
            const start = Date.now()
            const response = await fetch('https://your-domain.com/health.json')
            const responseTime = Date.now() - start
            
            const status = response.ok ? 'Healthy' : 'Error'
            document.getElementById('status').textContent = status
            document.getElementById('response-time').textContent = responseTime + 'ms'
            
            // Update every 30 seconds
            setTimeout(updateMetrics, 30000)
        }
        
        updateMetrics()
    </script>
</body>
</html>
```

### Recommended Dashboard Tools

1. **Grafana** - Advanced metrics visualization
2. **Datadog** - Full-stack monitoring
3. **New Relic** - Application performance monitoring
4. **Google Analytics** - User behavior tracking
5. **Custom Dashboard** - Simple HTML/React dashboard

## Incident Response

### Incident Response Workflow

```
Detection → Triage → Response → Resolution → Post-Mortem
```

**1. Detection (< 5 min)**
- Alert received
- Verify issue
- Assess severity
- Notify team

**2. Triage (< 10 min)**
- Identify root cause
- Determine impact
- Decide on action (fix forward vs rollback)
- Escalate if needed

**3. Response (< 30 min)**
- Execute fix or rollback
- Verify resolution
- Monitor stability
- Update stakeholders

**4. Resolution**
- Issue resolved
- Service stable
- Users notified
- Status updated

**5. Post-Mortem (within 48 hours)**
- Document timeline
- Root cause analysis
- Lessons learned
- Process improvements

### Incident Severity Levels

**P0 - Critical**
- Complete outage
- Data loss risk
- Security breach
- Response: Immediate, all hands

**P1 - High**
- Major features down
- Significant user impact (>50%)
- Performance collapse
- Response: Within 30 minutes

**P2 - Medium**
- Minor features down
- Some user impact (<50%)
- Performance degradation
- Response: Within 2 hours

**P3 - Low**
- Minor issues
- Minimal user impact
- Cosmetic bugs
- Response: Next business day

## Monitoring Checklist

### Daily
- [ ] Check Sentry for new errors
- [ ] Review performance metrics
- [ ] Check uptime status
- [ ] Review server logs
- [ ] Check deployment status

### Weekly
- [ ] Review error trends
- [ ] Performance comparison
- [ ] Capacity planning review
- [ ] Alert effectiveness review
- [ ] Update runbooks if needed

### Monthly
- [ ] Full monitoring audit
- [ ] Review all alerts
- [ ] Update thresholds
- [ ] Team training
- [ ] Process improvements

---

**Document Version:** 1.0.0  
**Created:** 2025-11-10  
**Owner:** Worker08  
**Review Schedule:** Quarterly or after major incidents
