# Load Testing for PrismQ Client Backend

This directory contains load testing scripts and documentation for the PrismQ Client Backend API.

## Overview

Load testing helps verify that the Backend API can handle expected traffic patterns and meets performance targets under stress conditions.

## Tools

- **Locust**: HTTP load testing framework
- **Python**: For writing load test scenarios

## Installation

```bash
# Install locust
pip install locust

# Verify installation
locust --version
```

## Running Load Tests

### Interactive Mode (Web UI)

```bash
# Start locust with web UI
locust -f locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure:
# - Number of users: 10
# - Spawn rate: 2 users/second
# - Host: http://localhost:8000

# Click "Start Swarming" to begin
```

### Headless Mode (Command Line)

```bash
# Run with 10 concurrent users for 1 minute
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 1m --headless

# Run with 50 users for 5 minutes
locust -f locustfile.py --host=http://localhost:8000 \
       --users 50 --spawn-rate 5 --run-time 5m --headless

# Run with custom output
locust -f locustfile.py --host=http://localhost:8000 \
       --users 20 --spawn-rate 2 --run-time 2m --headless \
       --csv=results --html=report.html
```

## Load Test Scenarios

### 1. WebClientUser (Default)

Simulates a typical user of the Web Client dashboard.

**Tasks** (weighted by frequency):
- Get modules (weight: 5) - Most common
- Get runs (weight: 4)
- Get module config (weight: 3)
- Health check (weight: 2)
- System stats (weight: 2)
- Launch module (weight: 1)
- Save config (weight: 1)
- Get run details (weight: 1)
- Get logs (weight: 1)

**Wait time**: 1-3 seconds between tasks

**Use case**: General dashboard usage

### 2. HighLoadUser

Simulates a user actively monitoring the dashboard (frequent polling).

**Tasks**:
- Poll runs list (weight: 10)
- Poll system stats (weight: 5)
- Health checks (weight: 3)

**Wait time**: 0.5-1 second between tasks

**Use case**: Active monitoring, live dashboards

### 3. BurstUser

Simulates burst traffic patterns (e.g., user opening multiple tabs).

**Tasks**:
- Burst of 4 requests in quick succession

**Wait time**: 5-10 seconds between bursts

**Use case**: Spike traffic handling

## Running Specific Scenarios

```bash
# Run only HighLoadUser scenario
locust -f locustfile.py --host=http://localhost:8000 \
       --users 10 --spawn-rate 2 --run-time 1m --headless \
       HighLoadUser

# Run only BurstUser scenario
locust -f locustfile.py --host=http://localhost:8000 \
       --users 5 --spawn-rate 1 --run-time 1m --headless \
       BurstUser
```

## Performance Targets

The load tests validate these performance targets:

### Response Times
- **GET requests**: <100ms average
- **POST /run**: <500ms (module launch)
- **POST /config**: <100ms (save config)

### Throughput
- **Requests per second**: 100+ RPS
- **Concurrent users**: 10+ without degradation

### Reliability
- **Success rate**: >99%
- **Error rate**: <1%

## Interpreting Results

### Success Criteria

✅ **Good Performance**:
```
Average Response Time: 45ms
Requests/sec: 150
Total Failures: 0
Failure rate: 0%
```

⚠️ **Marginal Performance**:
```
Average Response Time: 120ms  # Slightly over target
Requests/sec: 80               # Below target
Total Failures: 5
Failure rate: 0.5%             # Acceptable
```

❌ **Poor Performance**:
```
Average Response Time: 300ms  # Way over target
Requests/sec: 30              # Far below target
Total Failures: 150
Failure rate: 15%             # Unacceptable
```

### Key Metrics

1. **Average Response Time**: Should be <100ms for GET requests
2. **95th Percentile**: Should be <200ms
3. **99th Percentile**: Should be <500ms
4. **Failure Rate**: Should be <1%
5. **Requests/Second**: Should be >100 RPS

## Common Issues

### Issue: High Response Times

**Symptoms**: Average response time >200ms

**Possible Causes**:
- Database queries not optimized
- No caching
- CPU/memory constraints
- Too many concurrent runs

**Solutions**:
- Add caching for frequently accessed data
- Optimize database queries
- Add indexes
- Implement rate limiting

### Issue: Request Failures

**Symptoms**: >5% failure rate

**Possible Causes**:
- Concurrent run limit reached
- Resource exhaustion (CPU/memory)
- Database connection pool exhausted
- Timeouts

**Solutions**:
- Increase concurrent run limit
- Scale resources
- Increase connection pool size
- Adjust timeouts

### Issue: Degrading Performance

**Symptoms**: Response times increase over time

**Possible Causes**:
- Memory leaks
- Log file growth
- No cleanup of old data
- Resource accumulation

**Solutions**:
- Fix memory leaks
- Implement log rotation
- Add cleanup tasks
- Monitor resource usage

## Advanced Usage

### Custom Test Scenarios

Create your own test scenario in `locustfile.py`:

```python
class CustomUser(HttpUser):
    wait_time = between(1, 2)
    
    @task(10)
    def my_heavy_operation(self):
        """Your custom test."""
        self.client.get("/api/my-endpoint")
```

### Distributed Load Testing

Run load tests across multiple machines:

```bash
# On master machine
locust -f locustfile.py --master

# On worker machines
locust -f locustfile.py --worker --master-host=<master-ip>
```

### Performance Profiling

Combine with Python profilers:

```bash
# Profile the backend during load test
python -m cProfile -o profile.stats \
    -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# Then run locust in another terminal
# Analyze profile after test
python -m pstats profile.stats
```

## Best Practices

1. **Start Small**: Begin with low user counts and increase gradually
2. **Monitor**: Watch server resources (CPU, memory, disk) during tests
3. **Realistic Scenarios**: Model actual user behavior
4. **Cleanup**: Ensure tests clean up created resources
5. **Baseline**: Establish performance baseline before optimizations
6. **Iterate**: Test after each optimization to measure impact
7. **Document**: Record results and configuration for comparison

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: Load Tests
on: [push]
jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start Backend
        run: |
          cd Client/Backend
          uvicorn src.main:app --host 127.0.0.1 --port 8000 &
      - name: Run Load Test
        run: |
          pip install locust
          cd Client/_meta/tests/load
          locust -f locustfile.py --host=http://localhost:8000 \
                 --users 10 --spawn-rate 2 --run-time 1m --headless \
                 --csv=results
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: Client/_meta/tests/load/results_*
```

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [Load Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Performance Testing Guide](https://developer.mozilla.org/en-US/docs/Web/Performance)

## Support

For issues or questions about load testing:
- Review the [TESTING_GUIDE.md](../TESTING_GUIDE.md)
- Check the Backend [README.md](../../Backend/README.md)
- Open an issue in the GitHub repository
