# STORY-005: Story Workflow Orchestrator

**Phase**: 2 (Workflow Orchestration)  
**Priority**: High  
**Effort**: 3 days  
**Dependencies**: STORY-001, STORY-002, STORY-003  
**Assigned**: Worker02 (Python Specialist)  
**Status**: Blocked (waiting for Phase 1)  
**Created**: 2025-11-24

---

## Problem Statement

Create a workflow orchestrator that coordinates the Story generation loop (Stages 21-22):
- Stage 21: ExpertReview → decides PUBLISH or POLISH
- Stage 22: Polish (if needed) → applies improvements
- Loop: Polish → ExpertReview (until quality threshold met or max iterations reached)

The orchestrator must:
- Manage workflow state
- Coordinate between Review and Polish stages
- Track iterations
- Handle max iteration limits
- Persist state to database
- Provide progress callbacks
- Support resume from failure

---

## Current State

**No orchestrator exists**. The `expert_review.py` and `polish.py` modules work independently but there's no code to run them in the Stage 21 → 22 → 21 loop.

**What Exists**:
- ✅ `StoryExpertReviewer.review_story()` - Stage 21
- ✅ `StoryPolisher.polish_story()` - Stage 22
- ✅ Decision logic (publish vs polish)

**What's Missing**:
- ❌ Workflow coordinator/runner
- ❌ Iteration loop logic
- ❌ State persistence
- ❌ Progress tracking
- ❌ Failure recovery

---

## Acceptance Criteria

### Core Functionality
- [ ] Create `StoryWorkflowOrchestrator` class
- [ ] Implement `run_story_workflow(story_id, title, script, ...)` method
- [ ] Coordinate ExpertReview → Polish → ExpertReview loop
- [ ] Track iteration count (max: configurable, default: 3)
- [ ] Stop when decision == "publish" OR max iterations reached
- [ ] Return final story with all metadata

### State Management
- [ ] Track workflow state (review, polish, complete, failed)
- [ ] Persist state to database after each stage
- [ ] Support resume from interruption
- [ ] Store complete audit trail (all reviews, all polishes)
- [ ] Track quality progression (scores over iterations)

### Configuration
- [ ] Configurable max iterations (default: 3)
- [ ] Configurable quality threshold (default: 95)
- [ ] Configurable timeout per stage
- [ ] Configurable retry attempts per stage
- [ ] Support for different GPT models per stage

### Progress & Monitoring
- [ ] Callback system for progress updates
- [ ] Log each stage completion
- [ ] Track total time and costs
- [ ] Emit events for monitoring (start, stage_complete, iteration, complete, error)
- [ ] Return comprehensive workflow result

### Error Handling
- [ ] Handle ExpertReview failures gracefully
- [ ] Handle Polish failures gracefully
- [ ] Implement retry logic (3 attempts per stage)
- [ ] Save state before each stage (for recovery)
- [ ] Provide meaningful error messages

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**Analysis**: Orchestrator should coordinate workflow, not implement review/polish logic.

**Recommendation**: 
- Orchestrator = coordination only
- Delegate to ExpertReviewer and Polisher for actual work
- Separate state persistence into `WorkflowStateManager`

**Structure**:
```python
class StoryWorkflowOrchestrator:
    def __init__(self, reviewer, polisher, state_manager):
        self.reviewer = reviewer
        self.polisher = polisher
        self.state_manager = state_manager
```

### Open/Closed Principle (OCP) ✅
**Analysis**: Should be open for new workflow stages, closed for modification.

**Recommendation**: Use state machine pattern with extensible states:
```python
class WorkflowState(Enum):
    INITIAL = "initial"
    REVIEWING = "reviewing"
    POLISHING = "polishing"
    COMPLETE = "complete"
    FAILED = "failed"
```

### Liskov Substitution Principle (LSP) ✅
**Analysis**: Should work with any reviewer/polisher that implements the interface.

**Recommendation**: Define interfaces:
```python
class StoryReviewer(ABC):
    @abstractmethod
    def review_story(self, ...) -> ExpertReview:
        pass

class StoryPolisher(ABC):
    @abstractmethod
    def polish_story(self, ...) -> StoryPolish:
        pass
```

### Interface Segregation Principle (ISP) ✅
**Analysis**: Keep interfaces minimal and focused.

**Recommendation**: Separate concerns:
- `StoryReviewer` for review
- `StoryPolisher` for polish
- `WorkflowStateManager` for persistence
- `WorkflowProgressCallback` for monitoring

### Dependency Inversion Principle (DIP) ✅
**Analysis**: Orchestrator depends on abstractions, not concrete implementations.

**Recommendation**:
```python
class StoryWorkflowOrchestrator:
    def __init__(
        self,
        reviewer: StoryReviewer,
        polisher: StoryPolisher,
        state_manager: WorkflowStateManager
    ):
        ...
```

---

## Implementation Details

### Architecture

```
T/Story/Workflow/
├── __init__.py
├── orchestrator.py (main orchestrator)
├── state_manager.py (state persistence)
├── models.py (workflow data models)
└── _meta/
    └── tests/
        ├── test_orchestrator.py
        └── test_state_manager.py
```

### Key Classes

#### 1. WorkflowState & Models

**File**: `T/Story/Workflow/models.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowState(Enum):
    """Workflow execution state."""
    INITIAL = "initial"
    REVIEWING = "reviewing"
    POLISHING = "polishing"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class WorkflowIteration:
    """Single iteration of review + polish."""
    iteration_number: int
    review: Dict[str, Any]  # ExpertReview data
    polish: Optional[Dict[str, Any]] = None  # StoryPolish data
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
@dataclass
class WorkflowResult:
    """Complete workflow execution result."""
    story_id: str
    initial_title: str
    initial_script: str
    final_title: str
    final_script: str
    
    state: WorkflowState
    iterations: List[WorkflowIteration] = field(default_factory=list)
    
    total_reviews: int = 0
    total_polishes: int = 0
    
    initial_quality_score: int = 0
    final_quality_score: int = 0
    quality_improvement: int = 0
    
    decision: str = "unknown"  # "publish" or "polish" or "max_iterations"
    
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    total_cost: float = 0.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
```

#### 2. Workflow Orchestrator

**File**: `T/Story/Workflow/orchestrator.py`

```python
from typing import Optional, Callable, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowConfig:
    """Configuration for story workflow."""
    def __init__(
        self,
        max_iterations: int = 3,
        quality_threshold: int = 95,
        max_stage_retries: int = 3,
        stage_timeout_seconds: int = 300
    ):
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.max_stage_retries = max_stage_retries
        self.stage_timeout_seconds = stage_timeout_seconds

class StoryWorkflowOrchestrator:
    """Orchestrates the Story Review + Polish workflow loop."""
    
    def __init__(
        self,
        reviewer: StoryReviewer,
        polisher: StoryPolisher,
        state_manager: WorkflowStateManager,
        config: Optional[WorkflowConfig] = None
    ):
        self.reviewer = reviewer
        self.polisher = polisher
        self.state_manager = state_manager
        self.config = config or WorkflowConfig()
        
    def run_story_workflow(
        self,
        story_id: str,
        title: str,
        script: str,
        audience_context: Dict[str, Any],
        original_idea: str = "",
        local_review_summary: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, Dict], None]] = None
    ) -> WorkflowResult:
        """Execute complete story workflow (Review → Polish → Review loop).
        
        Args:
            story_id: Unique story identifier
            title: Current title
            script: Current script
            audience_context: Target audience info
            original_idea: Original story idea
            local_review_summary: Summary of local reviews (stages 1-20)
            progress_callback: Optional callback for progress updates
            
        Returns:
            WorkflowResult with final story and complete audit trail
        """
        logger.info(f"Starting story workflow for {story_id}")
        
        # Initialize result
        result = WorkflowResult(
            story_id=story_id,
            initial_title=title,
            initial_script=script,
            final_title=title,
            final_script=script,
            state=WorkflowState.INITIAL
        )
        
        # Save initial state
        self.state_manager.save_state(story_id, result)
        
        # Emit progress
        self._emit_progress(progress_callback, "workflow_started", {
            "story_id": story_id,
            "max_iterations": self.config.max_iterations
        })
        
        try:
            current_title = title
            current_script = script
            
            for iteration in range(1, self.config.max_iterations + 1):
                logger.info(f"Starting iteration {iteration}/{self.config.max_iterations}")
                
                # Create iteration record
                iteration_data = WorkflowIteration(iteration_number=iteration)
                
                # Stage 21: Expert Review
                result.state = WorkflowState.REVIEWING
                self.state_manager.save_state(story_id, result)
                
                review = self._run_expert_review(
                    story_id,
                    current_title,
                    current_script,
                    audience_context,
                    original_idea,
                    local_review_summary,
                    f"v{iteration}"
                )
                
                iteration_data.review = review.to_dict()
                result.total_reviews += 1
                
                # Track quality
                quality_score = review.overall_assessment.quality_score
                if iteration == 1:
                    result.initial_quality_score = quality_score
                result.final_quality_score = quality_score
                
                # Track cost
                if "_meta" in iteration_data.review:
                    result.total_cost += iteration_data.review["_meta"].get("cost_estimate", 0)
                
                self._emit_progress(progress_callback, "review_complete", {
                    "iteration": iteration,
                    "quality_score": quality_score,
                    "decision": review.decision.value
                })
                
                # Check decision
                if review.decision == ReviewDecision.PUBLISH:
                    logger.info(f"Decision: PUBLISH (score: {quality_score})")
                    result.decision = "publish"
                    iteration_data.completed_at = datetime.now()
                    result.iterations.append(iteration_data)
                    break
                
                # Stage 22: Polish
                logger.info(f"Decision: POLISH (score: {quality_score})")
                result.state = WorkflowState.POLISHING
                self.state_manager.save_state(story_id, result)
                
                polish = self._run_polish(
                    story_id,
                    current_title,
                    current_script,
                    review.to_dict(),
                    iteration,
                    audience_context,
                    original_idea
                )
                
                iteration_data.polish = polish.to_dict()
                result.total_polishes += 1
                
                # Update current story
                current_title = polish.polished_title
                current_script = polish.polished_script
                result.final_title = current_title
                result.final_script = current_script
                
                iteration_data.completed_at = datetime.now()
                result.iterations.append(iteration_data)
                
                self._emit_progress(progress_callback, "polish_complete", {
                    "iteration": iteration,
                    "changes_count": len(polish.change_log)
                })
                
                # Check if max iterations reached
                if iteration == self.config.max_iterations:
                    logger.warning(f"Max iterations ({self.config.max_iterations}) reached")
                    result.decision = "max_iterations_reached"
                    break
            
            # Workflow complete
            result.state = WorkflowState.COMPLETE
            result.completed_at = datetime.now()
            result.total_duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()
            result.quality_improvement = (
                result.final_quality_score - result.initial_quality_score
            )
            
            self.state_manager.save_state(story_id, result)
            
            self._emit_progress(progress_callback, "workflow_complete", {
                "story_id": story_id,
                "iterations": len(result.iterations),
                "final_quality": result.final_quality_score,
                "decision": result.decision
            })
            
            logger.info(f"Workflow complete: {result.decision}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            result.state = WorkflowState.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()
            self.state_manager.save_state(story_id, result)
            
            self._emit_progress(progress_callback, "workflow_failed", {
                "story_id": story_id,
                "error": str(e)
            })
            
            raise
    
    def _run_expert_review(
        self,
        story_id: str,
        title: str,
        script: str,
        audience_context: Dict[str, Any],
        original_idea: str,
        local_review_summary: Optional[Dict[str, Any]],
        version: str
    ) -> ExpertReview:
        """Run expert review with retry logic."""
        for attempt in range(1, self.config.max_stage_retries + 1):
            try:
                return self.reviewer.review_story(
                    title=title,
                    script=script,
                    audience_context=audience_context,
                    original_idea=original_idea,
                    story_id=story_id,
                    story_version=version,
                    local_review_summary=local_review_summary
                )
            except Exception as e:
                if attempt == self.config.max_stage_retries:
                    raise
                logger.warning(f"Review attempt {attempt} failed: {e}, retrying...")
                time.sleep(2 ** attempt)
    
    def _run_polish(
        self,
        story_id: str,
        title: str,
        script: str,
        review_data: Dict[str, Any],
        iteration: int,
        audience_context: Dict[str, Any],
        original_idea: str
    ) -> StoryPolish:
        """Run polish with retry logic."""
        for attempt in range(1, self.config.max_stage_retries + 1):
            try:
                return self.polisher.polish_story(
                    story_id=story_id,
                    current_title=title,
                    current_script=script,
                    expert_review_data=review_data,
                    iteration_number=iteration,
                    audience_context=audience_context,
                    original_idea=original_idea
                )
            except Exception as e:
                if attempt == self.config.max_stage_retries:
                    raise
                logger.warning(f"Polish attempt {attempt} failed: {e}, retrying...")
                time.sleep(2 ** attempt)
    
    def _emit_progress(
        self,
        callback: Optional[Callable],
        event: str,
        data: Dict[str, Any]
    ):
        """Emit progress event."""
        if callback:
            try:
                callback(event, data)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
```

#### 3. State Manager

**File**: `T/Story/Workflow/state_manager.py`

```python
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

class WorkflowStateManager:
    """Manages workflow state persistence."""
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, story_id: str, result: WorkflowResult):
        """Save workflow state to disk."""
        state_file = self.state_dir / f"{story_id}_workflow.json"
        state_file.write_text(json.dumps(result.to_dict(), indent=2))
    
    def load_state(self, story_id: str) -> Optional[WorkflowResult]:
        """Load workflow state from disk."""
        state_file = self.state_dir / f"{story_id}_workflow.json"
        if not state_file.exists():
            return None
        
        data = json.loads(state_file.read_text())
        return WorkflowResult.from_dict(data)
    
    def resume_workflow(self, story_id: str) -> Optional[WorkflowResult]:
        """Resume interrupted workflow."""
        result = self.load_state(story_id)
        if not result:
            return None
        
        if result.state in [WorkflowState.COMPLETE, WorkflowState.FAILED]:
            return result  # Already done
        
        # Can resume from REVIEWING or POLISHING state
        return result
```

---

## Testing Strategy

### Unit Tests

**File**: `T/Story/Workflow/_meta/tests/test_orchestrator.py`

```python
import pytest
from unittest.mock import Mock, patch
from T.Story.Workflow.orchestrator import StoryWorkflowOrchestrator, WorkflowConfig

class TestStoryWorkflowOrchestrator:
    def test_workflow_publish_first_iteration(self):
        """Test workflow that publishes on first review."""
        # Mock reviewer returns publish decision
        reviewer = Mock()
        review_result = Mock()
        review_result.decision = ReviewDecision.PUBLISH
        review_result.overall_assessment.quality_score = 96
        reviewer.review_story.return_value = review_result
        
        polisher = Mock()
        state_manager = Mock()
        
        orchestrator = StoryWorkflowOrchestrator(reviewer, polisher, state_manager)
        
        result = orchestrator.run_story_workflow(
            story_id="test-001",
            title="Test Title",
            script="Test script",
            audience_context={}
        )
        
        assert result.decision == "publish"
        assert result.total_reviews == 1
        assert result.total_polishes == 0
        assert len(result.iterations) == 1
    
    def test_workflow_polish_then_publish(self):
        """Test workflow that polishes once then publishes."""
        reviewer = Mock()
        # First review: needs polish
        review1 = Mock()
        review1.decision = ReviewDecision.POLISH
        review1.overall_assessment.quality_score = 88
        # Second review: publish
        review2 = Mock()
        review2.decision = ReviewDecision.PUBLISH
        review2.overall_assessment.quality_score = 96
        reviewer.review_story.side_effect = [review1, review2]
        
        polisher = Mock()
        polish_result = Mock()
        polish_result.polished_title = "Improved Title"
        polish_result.polished_script = "Improved script"
        polish_result.change_log = []
        polisher.polish_story.return_value = polish_result
        
        state_manager = Mock()
        
        orchestrator = StoryWorkflowOrchestrator(reviewer, polisher, state_manager)
        
        result = orchestrator.run_story_workflow(
            story_id="test-002",
            title="Test Title",
            script="Test script",
            audience_context={}
        )
        
        assert result.decision == "publish"
        assert result.total_reviews == 2
        assert result.total_polishes == 1
        assert len(result.iterations) == 2
    
    def test_workflow_max_iterations(self):
        """Test workflow stops at max iterations."""
        reviewer = Mock()
        review = Mock()
        review.decision = ReviewDecision.POLISH
        review.overall_assessment.quality_score = 90
        reviewer.review_story.return_value = review
        
        polisher = Mock()
        polish_result = Mock()
        polish_result.polished_title = "Title"
        polish_result.polished_script = "Script"
        polish_result.change_log = []
        polisher.polish_story.return_value = polish_result
        
        state_manager = Mock()
        
        config = WorkflowConfig(max_iterations=2)
        orchestrator = StoryWorkflowOrchestrator(reviewer, polisher, state_manager, config)
        
        result = orchestrator.run_story_workflow(
            story_id="test-003",
            title="Test Title",
            script="Test script",
            audience_context={}
        )
        
        assert result.decision == "max_iterations_reached"
        assert result.total_reviews == 2
        assert result.total_polishes == 2
```

---

## Definition of Done

### Code Complete
- [ ] `StoryWorkflowOrchestrator` implemented
- [ ] `WorkflowStateManager` implemented
- [ ] All models defined
- [ ] Retry logic working
- [ ] Progress callbacks working

### Testing Complete
- [ ] Unit tests >80% coverage
- [ ] Integration tests with real Review/Polish
- [ ] Error scenarios tested
- [ ] State persistence tested
- [ ] Resume functionality tested

### Documentation
- [ ] Docstrings complete
- [ ] Usage guide created
- [ ] Configuration reference
- [ ] State machine diagram

### Integration
- [ ] Works with STORY-001 (Review API)
- [ ] Works with STORY-002 (Polish API)
- [ ] Compatible with STORY-007 (DB integration)
- [ ] Ready for STORY-013 (Publishing integration)

---

## Related Issues

- **STORY-001**: GPT Review API (dependency)
- **STORY-002**: GPT Polish API (dependency)
- **STORY-006**: Iteration Loop Management (extends this)
- **STORY-007**: Database Integration (uses this orchestrator)
- **STORY-013**: Publishing Integration (uses this orchestrator)

---

**Status**: Blocked (Phase 1 must complete)  
**Created**: 2025-11-24  
**Owner**: Worker01  
**Reviewer**: Worker10
