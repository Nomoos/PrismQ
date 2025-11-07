"""
Load testing script for PrismQ Client Backend using Locust.

Usage:
    # Install locust first:
    pip install locust

    # Run load test:
    locust -f locustfile.py --host=http://localhost:8000

    # Or run headless with specific parameters:
    locust -f locustfile.py --host=http://localhost:8000 \
           --users 10 --spawn-rate 2 --run-time 1m --headless

Performance Targets:
    - API response time: <100ms for GET requests
    - Module launch time: <500ms
    - Concurrent runs: Support 10+ without degradation
    - Requests per second: 100+
"""

from locust import HttpUser, task, between, events


class WebClientUser(HttpUser):
    """Simulates a user of the PrismQ Web Client."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - setup data."""
        self.run_ids = []
        self.module_ids = []
        
        # Get available modules
        response = self.client.get("/api/modules")
        if response.status_code == 200:
            modules = response.json().get("modules", [])
            self.module_ids = [m["id"] for m in modules]
    
    @task(5)
    def get_modules(self):
        """List available modules (most common operation)."""
        with self.client.get("/api/modules", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(4)
    def get_runs(self):
        """List runs."""
        with self.client.get("/api/runs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(3)
    def get_module_config(self):
        """Get module configuration."""
        if not self.module_ids:
            return
        
        module_id = self.module_ids[0]  # Use first module
        with self.client.get(
            f"/api/modules/{module_id}/config",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def health_check(self):
        """Check API health."""
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def system_stats(self):
        """Get system statistics."""
        with self.client.get("/api/system/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def launch_module(self):
        """Launch a module (less frequent but important operation)."""
        if not self.module_ids:
            return
        
        module_id = self.module_ids[0]
        payload = {
            "parameters": {"max_results": 10},
            "save_config": False
        }
        
        with self.client.post(
            f"/api/modules/{module_id}/run",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 202:
                # Track run ID for cleanup
                run_data = response.json()
                if "run_id" in run_data:
                    self.run_ids.append(run_data["run_id"])
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def save_config(self):
        """Save module configuration."""
        if not self.module_ids:
            return
        
        module_id = self.module_ids[0]
        payload = {
            "parameters": {
                "max_results": 50,
                "category": "Gaming"
            }
        }
        
        with self.client.post(
            f"/api/modules/{module_id}/config",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def get_run_details(self):
        """Get details of a run."""
        if not self.run_ids:
            return
        
        run_id = self.run_ids[-1]  # Get most recent run
        with self.client.get(f"/api/runs/{run_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def get_logs(self):
        """Get logs for a run."""
        if not self.run_ids:
            return
        
        run_id = self.run_ids[-1]
        with self.client.get(
            f"/api/runs/{run_id}/logs?tail=100",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    def on_stop(self):
        """Called when a user stops - cleanup."""
        # Cancel any runs we created
        for run_id in self.run_ids:
            try:
                self.client.delete(f"/api/runs/{run_id}")
            except:
                pass  # Ignore cleanup errors


# Event handlers for custom metrics

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom metrics for each request."""
    if exception:
        return
    
    # Alert if response time exceeds targets
    if request_type == "GET" and response_time > 100:
        print(f"⚠️  GET {name} took {response_time:.2f}ms (target: <100ms)")
    elif request_type == "POST" and "run" in name and response_time > 500:
        print(f"⚠️  POST {name} took {response_time:.2f}ms (target: <500ms)")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("\n" + "="*60)
    print("PrismQ Client Backend - Load Test Starting")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    stats = environment.stats
    
    print("\n" + "="*60)
    print("PrismQ Client Backend - Load Test Results")
    print("="*60)
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.current_rps:.2f}")
    print("="*60)
    
    # Check if performance targets were met
    passed = True
    
    if stats.total.avg_response_time > 100:
        print(f"❌ Average response time {stats.total.avg_response_time:.2f}ms exceeds 100ms target")
        passed = False
    else:
        print(f"✅ Average response time {stats.total.avg_response_time:.2f}ms meets target")
    
    if stats.total.num_failures > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        if failure_rate > 1:
            print(f"❌ Failure rate {failure_rate:.2f}% exceeds 1% target")
            passed = False
        else:
            print(f"✅ Failure rate {failure_rate:.2f}% acceptable")
    
    print("="*60 + "\n")


# Custom load test scenarios

class HighLoadUser(HttpUser):
    """Simulates high-frequency polling user (e.g., active dashboard)."""
    
    wait_time = between(0.5, 1)  # Poll frequently
    
    @task(10)
    def poll_runs(self):
        """Frequent polling of runs list."""
        self.client.get("/api/runs?limit=20")
    
    @task(5)
    def poll_system_stats(self):
        """Poll system statistics."""
        self.client.get("/api/system/stats")
    
    @task(3)
    def check_health(self):
        """Health checks."""
        self.client.get("/api/health")


class BurstUser(HttpUser):
    """Simulates burst traffic (e.g., multiple tabs opening)."""
    
    wait_time = between(5, 10)  # Long wait between bursts
    
    @task
    def burst_requests(self):
        """Make multiple requests in quick succession."""
        self.client.get("/api/modules")
        self.client.get("/api/runs")
        self.client.get("/api/system/stats")
        self.client.get("/api/health")
