# Issue #338: Research Scheduling Strategy Performance

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 09 - Research Engineer  
**Status**: Partially Complete - Framework Ready  
**Priority**: High  
**Duration**: Part of #337 (1 week total)  
**Dependencies**: #327 (Queue Scheduling Strategies - MUST COMPLETE FIRST for benchmarking)

---

## Objective

Conduct comprehensive research and performance analysis of the four scheduling strategies (FIFO, LIFO, Priority, Weighted Random) implemented in #327, evaluating fairness characteristics, starvation risks, and use-case recommendations.

---

## ✅ Implementation Progress

**Completed Components** (ready to use now):
- ✅ `fairness_metrics.py` - Statistical analysis module (384 lines)
  - Gini coefficient calculation
  - Jain's fairness index calculation
  - Percentile calculations (P50, P95, P99)
  - Comprehensive wait time statistics
  - Starvation risk analysis
  - Probability distribution analysis
- ✅ `test_fairness_metrics.py` - Comprehensive unit tests (30 tests, all passing)
- ✅ `scheduling_strategy_benchmark.py` - Benchmark framework (518 lines)
- ✅ `SCHEDULING_STRATEGY_COMPARISON.md` - Report template (197 lines)
- ✅ `ISSUE_338_README.md` - Documentation

**Blocked Components** (waiting for #327):
- ⏳ Actual strategy benchmarking
- ⏳ Performance measurements
- ⏳ Probability distribution validation
- ⏳ Final report with empirical data

**See**: `_meta/research/ISSUE_338_README.md` for details

---

## ⚠️ Blocker Status

**This issue is BLOCKED by #327** (Queue Scheduling Strategies)

**Reason**: Issue #327 must be fully implemented by Worker 04 before this research can begin. Worker 09 needs:
- All 4 scheduling strategies implemented (FIFO, LIFO, Priority, Weighted Random)
- Working code to benchmark
- Integration with core queue infrastructure

**Action**: Wait for Worker 04 to complete #327, then begin research work.

**Estimated Start**: After #327 completion (Week 2-3 of overall timeline)

---

## Background

From #320 analysis and #327 requirements:
- Four scheduling strategies provide different ordering guarantees
- Each strategy has different fairness characteristics
- Some strategies risk task starvation
- Production use requires understanding tradeoffs

**Goal**: Provide empirical data and recommendations to guide strategy selection for different use cases.

---

## Research Questions

### 1. Strategy Performance Comparison

**Questions**:
- What is the claim latency for each strategy?
- How does throughput differ between strategies?
- Which strategy has the most consistent performance?
- Do any strategies have unexpected overhead?

**Method**: Benchmark all 4 strategies under identical conditions

### 2. Fairness Analysis

**Questions**:
- How fair is task distribution in each strategy?
- Does FIFO truly maintain submission order under load?
- How much do priorities affect selection in Priority strategy?
- What is the actual probability distribution in Weighted Random?

**Method**: Track selection order and probability across many tasks

### 3. Starvation Risk Evaluation

**Questions**:
- Which strategies can cause complete task starvation?
- How quickly can low-priority tasks become starved?
- Does Weighted Random truly prevent starvation?
- What mitigation strategies can prevent starvation?

**Method**: Create scenarios with mixed priority tasks, measure wait times

### 4. Use Case Recommendations

**Questions**:
- When should each strategy be used?
- Can multiple strategies coexist safely?
- How should priorities be assigned for different task types?
- What are the edge cases for each strategy?

**Method**: Analyze real-world scenarios and match to strategy characteristics

---

## Testing Plan

### Test Environment

**Hardware**:
- OS: Windows 10/11
- GPU: NVIDIA RTX 5090 (32GB VRAM)
- CPU: AMD Ryzen processor
- RAM: 64GB DDR5
- Storage: NVMe SSD

**Software**:
- Python 3.10.x
- SQLite with WAL mode (from #337 tuning)
- Queue implementation from #327

### Test Scenarios

#### Scenario 1: Strategy Performance Baseline
```
Test each strategy independently:

For each strategy in [FIFO, LIFO, Priority, Weighted Random]:
  1. Enqueue 10,000 tasks with mixed priorities (1, 10, 50, 100)
  2. Single worker claims and processes tasks
  3. Measure: claim latency (P50, P95, P99), throughput, CPU usage
```

#### Scenario 2: Fairness Under Load
```
Test fair distribution:

For each strategy:
  1. Enqueue 1,000 tasks with creation timestamps
  2. Track: selection order, wait time per task
  3. Compute: fairness metrics (Gini coefficient, Jain's fairness index)
```

#### Scenario 3: Starvation Test
```
Test starvation scenarios:

Priority Strategy:
  1. Enqueue 100 high-priority tasks (priority=1)
  2. Enqueue 100 low-priority tasks (priority=100)
  3. Continuously add high-priority tasks during test
  4. Measure: max wait time for low-priority tasks

Weighted Random Strategy:
  1. Same setup as Priority strategy
  2. Verify: low-priority tasks eventually get selected
  3. Compare: starvation behavior vs Priority strategy
```

#### Scenario 4: Mixed Strategy Workers
```
Multiple workers with different strategies:

Setup:
  - Worker 1: FIFO strategy
  - Worker 2: Priority strategy
  - Worker 3: Weighted Random strategy

Test:
  1. Enqueue 3,000 tasks with mixed priorities
  2. All workers claim tasks simultaneously
  3. Verify: no conflicts, correct strategy-specific behavior
  4. Measure: task distribution across workers
```

#### Scenario 5: Strategy Switching
```
Test runtime strategy changes:

Setup:
  - Single worker starts with FIFO strategy
  
Test:
  1. Process 100 tasks with FIFO
  2. Switch to Priority strategy mid-test
  3. Process 100 tasks with Priority
  4. Switch to Weighted Random
  5. Process 100 tasks with Weighted Random
  6. Verify: smooth transitions, no task loss
  7. Measure: strategy switching overhead
```

---

## Deliverables

### 1. Strategy Comparison Report

**File**: `_meta/research/SCHEDULING_STRATEGY_COMPARISON.md`

**Sections**:
- Executive Summary
- Test Methodology
- Performance Benchmarks (tables and charts)
- Fairness Analysis Results
- Starvation Risk Assessment
- Strategy Switching Analysis
- Recommendations by Use Case

**Format**: Markdown with tables, code examples, and charts (optional)

### 2. Fairness Analysis

**File**: Part of comparison report

**Metrics**:
- Gini Coefficient (0 = perfect equality, 1 = complete inequality)
- Jain's Fairness Index (0 = unfair, 1 = perfectly fair)
- Wait time distribution (P50, P95, P99)
- Selection probability by priority level

**Expected Results Format** (actual values to be determined through research):
```markdown
| Strategy | Gini Coefficient | Jain's Index | P95 Wait Time |
|----------|------------------|--------------|---------------|
| FIFO     | TBD             | TBD          | TBD           |
| LIFO     | TBD             | TBD          | TBD           |
| Priority | TBD             | TBD          | TBD           |
| W.Random | TBD             | TBD          | TBD           |
```

### 3. Starvation Risk Evaluation

**File**: Part of comparison report

**Analysis**:
```markdown
#### FIFO - Starvation Risk: LOW
- All tasks eventually processed in order
- Risk: Very old tasks if queue grows faster than processing
- Mitigation: Monitor queue depth, scale workers

#### LIFO - Starvation Risk: HIGH
- Old tasks may never be processed
- Risk: Continuous new tasks completely starve old ones
- Mitigation: Use only for ephemeral tasks (e.g., user cancellations)

#### Priority - Starvation Risk: HIGH for low priority
- Low-priority tasks starved by constant high-priority influx
- Risk: Priority 100 tasks never run if priority 1 tasks keep coming
- Mitigation: Age-based priority boost, time-based fairness

#### Weighted Random - Starvation Risk: LOW
- Probabilistic selection ensures eventual processing
- Risk: Low-priority tasks delayed but not completely starved
- Mitigation: None needed (design prevents starvation)
```

### 4. Recommendations by Use Case

**File**: Part of comparison report

**Recommendations**:
```markdown
### Background Processing (Data Imports, ETL)
**Recommended**: FIFO
- Fair processing order
- Predictable completion
- Acceptable for non-urgent tasks

### User-Triggered Actions (API Calls)
**Recommended**: Priority or Weighted Random
- Priority: For strict SLA requirements
- Weighted Random: For balanced responsiveness

### Latest-First Processing (Cancel Previous)
**Recommended**: LIFO
- Only if old tasks can be safely discarded
- Example: Preview generation (latest overwrites)

### Mixed Workload (Critical + Background)
**Recommended**: Weighted Random
- Prevents complete starvation
- Still favors high priority
- Best overall fairness

### Multiple Worker Types
**Recommended**: Different strategies per worker
- Critical workers: Priority strategy
- Background workers: FIFO strategy
- Balanced workers: Weighted Random strategy
```

---

## Metrics to Collect

### Performance Metrics
- Claim latency by strategy (P50, P95, P99)
- Throughput (tasks/second) by strategy
- CPU usage by strategy
- Strategy switching overhead (if applicable)

### Fairness Metrics
- Gini Coefficient (wealth inequality measure)
- Jain's Fairness Index (network fairness measure)
- Wait time distribution by priority level
- Selection probability vs expected probability

### Starvation Metrics
- Maximum wait time by priority level
- Percentage of tasks waiting >5 minutes
- Percentage of tasks waiting >1 hour
- Time until first selection by priority

---

## Analysis Framework

### Fairness Calculations

```python
def calculate_gini_coefficient(wait_times):
    """
    Calculate Gini coefficient for wait time distribution.
    
    0.0 = perfect equality (all tasks wait same time)
    1.0 = complete inequality (one task waits infinitely)
    """
    sorted_times = sorted(wait_times)
    n = len(sorted_times)
    cumsum = 0
    for i, t in enumerate(sorted_times):
        cumsum += (2 * i - n + 1) * t
    return cumsum / (n * sum(sorted_times))

def calculate_jains_fairness_index(wait_times):
    """
    Calculate Jain's Fairness Index.
    
    Closer to 1.0 = more fair
    Closer to 0.0 = less fair
    """
    n = len(wait_times)
    sum_times = sum(wait_times)
    sum_squares = sum(t**2 for t in wait_times)
    return (sum_times ** 2) / (n * sum_squares)
```

### Probability Analysis (Weighted Random)

```python
def analyze_weighted_random_distribution(results):
    """
    Verify weighted random matches expected probabilities.
    
    Expected probability for priority p:
      P(p) = (1 / (p + 1)) / sum(1 / (pi + 1) for all priorities)
    """
    # Count selections by priority
    selections_by_priority = count_selections(results)
    
    # Calculate expected probabilities
    expected_prob = calculate_expected_probabilities(results)
    
    # Compare actual vs expected
    for priority, actual_count in selections_by_priority.items():
        actual_prob = actual_count / len(results)
        expected = expected_prob[priority]
        deviation = abs(actual_prob - expected) / expected * 100
        
        print(f"Priority {priority}:")
        print(f"  Expected: {expected:.2%}")
        print(f"  Actual:   {actual_prob:.2%}")
        print(f"  Deviation: {deviation:.1f}%")
```

---

## Expected Outcomes

### Performance Expectations (Hypothetical - To Be Validated)

*Note: These are expected ranges based on #327 design. Actual results will be determined through benchmarking.*

| Strategy | Claim Latency (P95) | Throughput Target | Expected Fairness |
|----------|---------------------|-------------------|-------------------|
| FIFO     | <10ms              | >500 tasks/min    | High (age-based)  |
| LIFO     | <10ms              | >500 tasks/min    | Low (reverse)     |
| Priority | <15ms              | >300 tasks/min    | By priority level |
| W.Random | <20ms              | >300 tasks/min    | Probabilistic     |

### Starvation Risk Summary

| Strategy | Low Priority Wait | Starvation Risk | Recommended For |
|----------|-------------------|-----------------|-----------------|
| FIFO     | Bounded           | ⚠️ Low         | Background jobs |
| LIFO     | Unbounded         | 🔴 High        | Ephemeral tasks |
| Priority | Unbounded         | 🔴 High        | SLA-critical    |
| W.Random | Long but bounded  | ✅ Low         | Mixed workload  |

---

## Timeline

### Days 1-2: Setup and Baseline (Part of #337 Week)
- [ ] Verify #327 implementation complete
- [ ] Create benchmark harness
- [ ] Run baseline performance tests
- [ ] Validate metric collection

### Days 3-4: Fairness and Starvation Tests
- [ ] Fairness analysis tests
- [ ] Starvation scenario tests
- [ ] Probability distribution tests
- [ ] Mixed strategy tests

### Days 5-7: Analysis and Documentation
- [ ] Statistical analysis
- [ ] Create comparison tables
- [ ] Write recommendations
- [ ] Review with team
- [ ] Finalize report

---

## Success Criteria

- [ ] #327 implementation verified and working
- [ ] All 4 strategies benchmarked
- [ ] Fairness metrics calculated for each strategy
- [ ] Starvation scenarios tested
- [ ] Weighted random probability distribution verified
- [ ] Strategy comparison report complete
- [ ] Use case recommendations documented
- [x] Team review completed
- [ ] Findings integrated into #335 (Documentation)

---

## Integration Points

### Depends On
- **#327: Queue Scheduling Strategies (BLOCKER)** - Implementation must be complete
- #321: Core Infrastructure - Database and schema
- #337: SQLite Concurrency Tuning - Optimal PRAGMA settings

### Feeds Into
- #335: Comprehensive Documentation - Strategy selection guide
- #339: Integration with BackgroundTaskManager - Strategy configuration
- Future workers: Strategy selection decisions

---

## Tools and Scripts

### Benchmark Script Structure

```python
# _meta/research/scheduling_strategy_benchmark.py

from typing import Dict, List
from enum import Enum
import time
import statistics

class StrategyBenchmark:
    """Benchmark scheduling strategies."""
    
    def __init__(self, queue_db_path):
        self.queue = SQLiteQueue(queue_db_path)
        
    def benchmark_strategy(self, strategy: SchedulingStrategy):
        """Benchmark a single strategy."""
        
    def measure_fairness(self, strategy: SchedulingStrategy):
        """Measure fairness metrics."""
        
    def test_starvation(self, strategy: SchedulingStrategy):
        """Test starvation scenarios."""
        
    def analyze_probability_distribution(self):
        """Analyze weighted random distribution."""
        
    def generate_comparison_report(self):
        """Generate markdown comparison report."""
```

---

## Acceptance Criteria

- [ ] Blocker #327 completed and verified
- [ ] All 4 scheduling strategies benchmarked
- [ ] Fairness analysis complete (Gini, Jain's index)
- [ ] Starvation risks documented for each strategy
- [ ] Weighted random probability distribution validated
- [ ] Use case recommendations written
- [ ] Comparison report published
- [x] Team review and approval received
- [ ] Recommendations integrated into documentation

---

## Resources

- Issue #327: Queue Scheduling Strategies (implementation reference)
- Issue #337: SQLite Concurrency Tuning (performance baseline)
- [Gini Coefficient](https://en.wikipedia.org/wiki/Gini_coefficient)
- [Jain's Fairness Index](https://en.wikipedia.org/wiki/Fairness_measure#Jain's_fairness_index)
- Queue scheduling research papers
- Python `statistics` module

---

**Status**: ⛔ Blocked by #327  
**Assigned**: Worker 09 - Research Engineer  
**Labels**: `research`, `performance`, `scheduling`, `analysis`, `blocked`

---

## Notes

- This issue is part of Worker 09's overall research assignment along with #337
- The two issues together constitute 1 week of research work
- Cannot begin until Worker 04 completes #327
- Results will inform production deployment strategy selection
- Critical for ensuring fair task processing in production
