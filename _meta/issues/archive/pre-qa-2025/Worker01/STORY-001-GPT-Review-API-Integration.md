# STORY-001: GPT API Integration for ExpertReview

**Phase**: 1 (GPT Integration - MVP)  
**Priority**: Critical  
**Effort**: 2 days  
**Dependencies**: STORY-003 (Prompt Templates)  
**Assigned**: Worker08 (AI/ML Specialist)  
**Status**: New  
**Created**: 2025-11-24

---

## Problem Statement

The `StoryExpertReviewer` class in `T/Story/ExpertReview/expert_review.py` currently uses simulated review logic (`_simulate_expert_review`). We need to replace this with real GPT API integration to provide actual expert-level story reviews.

The GPT integration must:
- Call OpenAI API with properly structured prompts
- Parse structured responses (JSON format)
- Handle API errors and rate limits
- Track token usage and costs
- Maintain quality thresholds

---

## Current State

**File**: `T/Story/ExpertReview/expert_review.py`

**Existing Implementation**:
```python
class StoryExpertReviewer:
    def review_story(self, title, script, audience_context, ...):
        # Creates review object
        review = ExpertReview(...)
        
        # Currently calls simulation
        review = self._simulate_expert_review(review)
        
        return review
    
    def _simulate_expert_review(self, review):
        # Placeholder logic - needs real GPT integration
        ...
```

**What Works**:
- ✅ Data structures for review results
- ✅ Review decision logic (publish vs polish)
- ✅ Improvement suggestion tracking
- ✅ Quality scoring framework

**What's Missing**:
- ❌ Real GPT API calls
- ❌ Prompt construction
- ❌ Response parsing and validation
- ❌ Error handling for API failures
- ❌ Token counting and cost tracking

---

## Acceptance Criteria

### Functional Requirements
- [ ] Replace `_simulate_expert_review()` with `_perform_gpt_review()`
- [ ] Integrate OpenAI Python SDK (openai>=1.0.0)
- [ ] Construct expert review prompt from template (from STORY-003)
- [ ] Call GPT API with structured output format (JSON mode)
- [ ] Parse GPT response into `ExpertReview` dataclass
- [ ] Validate all required fields are present in response
- [ ] Handle missing or malformed response fields gracefully
- [ ] Set appropriate model parameters (temperature, max_tokens)

### Error Handling
- [ ] Handle OpenAI API rate limit errors (429)
- [ ] Handle OpenAI API server errors (500, 503)
- [ ] Handle network timeouts and connection errors
- [ ] Implement exponential backoff for retries (3 attempts)
- [ ] Log all API errors with context
- [ ] Provide meaningful error messages to caller

### Cost & Performance
- [ ] Track token usage (prompt + completion)
- [ ] Calculate cost per review (model-specific pricing)
- [ ] Add cost to review metadata
- [ ] Log token usage for monitoring
- [ ] Implement max_tokens limit to prevent runaway costs
- [ ] Support model selection (gpt-4, gpt-4-turbo, gpt-3.5-turbo)

### Configuration
- [ ] Read API key from environment variable (OPENAI_API_KEY)
- [ ] Support custom API endpoint (for Azure OpenAI)
- [ ] Make model selection configurable
- [ ] Make temperature configurable (default: 0.2 for consistency)
- [ ] Make max_tokens configurable (default: 2000)
- [ ] Make retry attempts configurable (default: 3)

### Testing
- [ ] Unit tests for successful review
- [ ] Unit tests for API error scenarios
- [ ] Unit tests for malformed responses
- [ ] Unit tests for token counting
- [ ] Integration test with real OpenAI API (optional)
- [ ] Mock tests for CI/CD pipeline
- [ ] Test coverage >80%

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**Analysis**: The `StoryExpertReviewer` class should focus solely on coordinating the review process. Extract API-specific logic into a separate `OpenAIClient` or `GPTAdapter` class.

**Recommendation**: Create `T/Story/ExpertReview/src/gpt_client.py` with:
- `GPTClient` class for raw API interactions
- `GPTReviewAdapter` class for review-specific formatting

**Benefit**: Clear separation between review logic and API interaction.

### Open/Closed Principle (OCP) ✅
**Analysis**: Should be open for extension (support different LLM providers) but closed for modification.

**Recommendation**: 
- Define abstract `LLMProvider` interface
- Implement `OpenAIProvider` as concrete implementation
- Allow future providers (Anthropic, Cohere, etc.) without modifying core

**Benefit**: Can swap LLM providers without changing `StoryExpertReviewer`.

### Liskov Substitution Principle (LSP) ✅
**Analysis**: If we define `LLMProvider` interface, all implementations must be interchangeable.

**Recommendation**: Ensure all providers return the same `ExpertReview` structure.

**Benefit**: Provider-agnostic review logic.

### Interface Segregation Principle (ISP) ✅
**Analysis**: Keep LLM provider interface focused on review needs only.

**Recommendation**: Define minimal interface:
```python
class LLMProvider(ABC):
    @abstractmethod
    def review_story(self, prompt: str, config: Dict) -> Dict[str, Any]:
        pass
```

**Benefit**: Providers implement only what's needed for reviews.

### Dependency Inversion Principle (DIP) ✅
**Analysis**: `StoryExpertReviewer` should depend on abstraction (interface) not concrete OpenAI implementation.

**Recommendation**: 
```python
class StoryExpertReviewer:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
```

**Benefit**: Easy to test with mock providers, easy to swap implementations.

---

## Implementation Details

### Recommended Architecture

```
T/Story/ExpertReview/
├── expert_review.py (main interface - unchanged externally)
├── src/
│   ├── gpt_client.py (NEW - OpenAI API interactions)
│   ├── llm_provider.py (NEW - Abstract interface)
│   └── openai_provider.py (NEW - OpenAI implementation)
└── _meta/
    └── tests/
        ├── test_expert_review.py (update)
        ├── test_gpt_client.py (NEW)
        └── test_openai_provider.py (NEW)
```

### Key Classes

#### 1. `LLMProvider` (Abstract Base)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def review_story(
        self, 
        prompt: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call LLM for story review.
        
        Returns:
            Structured review data as dict
        """
        pass
```

#### 2. `OpenAIProvider` (Concrete Implementation)
```python
import openai
from typing import Dict, Any
import json
import time

class OpenAIProvider(LLMProvider):
    def __init__(
        self, 
        api_key: str,
        model: str = "gpt-4",
        max_retries: int = 3
    ):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
    
    def review_story(
        self, 
        prompt: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call OpenAI API with retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert story reviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=config.get("temperature", 0.2),
                    max_tokens=config.get("max_tokens", 2000)
                )
                
                # Parse response
                result = json.loads(response.choices[0].message.content)
                
                # Add metadata
                result["_meta"] = {
                    "model": self.model,
                    "tokens_prompt": response.usage.prompt_tokens,
                    "tokens_completion": response.usage.completion_tokens,
                    "tokens_total": response.usage.total_tokens,
                    "cost_estimate": self._calculate_cost(response.usage)
                }
                
                return result
                
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            
            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
    
    def _calculate_cost(self, usage) -> float:
        """Calculate estimated cost in USD."""
        # GPT-4 pricing (example)
        prompt_cost = usage.prompt_tokens * 0.00003
        completion_cost = usage.completion_tokens * 0.00006
        return prompt_cost + completion_cost
```

#### 3. Update `StoryExpertReviewer`
```python
class StoryExpertReviewer:
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        publish_threshold: int = 95
    ):
        self.llm_provider = llm_provider or self._default_provider()
        self.publish_threshold = publish_threshold
    
    def _default_provider(self) -> LLMProvider:
        """Create default OpenAI provider."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIProvider(api_key=api_key, model="gpt-4")
    
    def review_story(self, title, script, audience_context, ...) -> ExpertReview:
        # Build prompt (use template from STORY-003)
        prompt = self._build_review_prompt(title, script, audience_context, ...)
        
        # Call LLM
        config = {
            "temperature": 0.2,
            "max_tokens": 2000
        }
        response_data = self.llm_provider.review_story(prompt, config)
        
        # Parse into ExpertReview
        review = self._parse_review_response(response_data, title, script, ...)
        
        return review
```

### Prompt Structure (Will be detailed in STORY-003)

```python
def _build_review_prompt(self, title, script, audience_context, ...):
    return f"""
    Review the following story for professional quality.
    
    **Title**: {title}
    
    **Script**: {script}
    
    **Audience**: {audience_context}
    
    **Original Idea**: {original_idea}
    
    Provide a comprehensive review in JSON format with:
    - overall_assessment: {{ready_for_publishing, quality_score, confidence}}
    - story_coherence: {{score, feedback, title_script_alignment}}
    - audience_fit: {{score, feedback, demographic_match}}
    - professional_quality: {{score, feedback, production_ready}}
    - platform_optimization: {{score, feedback, platform_perfect}}
    - improvement_suggestions: [{{component, priority, suggestion, impact, estimated_effort}}]
    - decision: "publish" or "polish"
    """
```

---

## Testing Strategy

### Unit Tests

**File**: `T/Story/ExpertReview/_meta/tests/test_openai_provider.py`

```python
import pytest
from unittest.mock import Mock, patch
from T.Story.ExpertReview.src.openai_provider import OpenAIProvider

class TestOpenAIProvider:
    def test_successful_review(self):
        """Test successful API call and response parsing."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        
        # Mock OpenAI response
        with patch.object(provider.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices[0].message.content = '{"quality_score": 95}'
            mock_response.usage.prompt_tokens = 500
            mock_response.usage.completion_tokens = 300
            mock_response.usage.total_tokens = 800
            mock_create.return_value = mock_response
            
            result = provider.review_story("test prompt", {})
            
            assert result["quality_score"] == 95
            assert result["_meta"]["tokens_total"] == 800
    
    def test_rate_limit_retry(self):
        """Test exponential backoff on rate limit."""
        provider = OpenAIProvider(api_key="test-key", max_retries=3)
        
        with patch.object(provider.client.chat.completions, 'create') as mock_create:
            # Fail twice, succeed third time
            mock_create.side_effect = [
                openai.RateLimitError("Rate limit"),
                openai.RateLimitError("Rate limit"),
                mock_success_response
            ]
            
            result = provider.review_story("test prompt", {})
            
            assert mock_create.call_count == 3
            assert result is not None
    
    def test_cost_calculation(self):
        """Test token cost calculation."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        
        usage = Mock()
        usage.prompt_tokens = 1000
        usage.completion_tokens = 500
        
        cost = provider._calculate_cost(usage)
        
        assert cost == 0.06  # (1000 * 0.00003) + (500 * 0.00006)
```

### Integration Tests (Optional - requires real API key)

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="No API key")
def test_real_openai_review():
    """Integration test with real OpenAI API."""
    provider = OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-3.5-turbo"  # Cheaper for testing
    )
    
    test_prompt = "Review this test story..."
    result = provider.review_story(test_prompt, {})
    
    assert "quality_score" in result
    assert "_meta" in result
    assert result["_meta"]["tokens_total"] > 0
```

---

## Definition of Done

### Code Complete
- [ ] `LLMProvider` interface defined
- [ ] `OpenAIProvider` implemented with full error handling
- [ ] `StoryExpertReviewer` updated to use provider
- [ ] All error scenarios handled
- [ ] Token counting and cost tracking working
- [ ] Logging added for monitoring

### Testing Complete
- [ ] Unit tests written and passing
- [ ] Test coverage >80%
- [ ] Integration tests added (optional, manual run)
- [ ] Mock tests for CI/CD
- [ ] Error scenarios tested

### Documentation Complete
- [ ] Docstrings for all new classes and methods
- [ ] README updated with GPT integration details
- [ ] Configuration guide added (API keys, models)
- [ ] Cost estimation documentation
- [ ] Error handling guide

### Review Complete
- [ ] Code reviewed by Worker10
- [ ] SOLID principles validated
- [ ] Security review (API key handling)
- [ ] Performance review (token limits)

### Integration Verified
- [ ] Works with existing `expert_review.py` interface
- [ ] Compatible with STORY-003 (prompts)
- [ ] Ready for STORY-005 (orchestrator) integration
- [ ] No breaking changes to public API

---

## Related Issues

- **STORY-003**: Prompt Engineering (dependency - need templates)
- **STORY-002**: GPT Polish API (similar implementation)
- **STORY-005**: Workflow Orchestrator (will use this)
- **STORY-010**: Cost Tracking (extends this work)

---

## Resources

### Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [JSON Mode](https://platform.openai.com/docs/guides/text-generation/json-mode)

### Pricing
- [OpenAI Pricing](https://openai.com/pricing)
- GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
- GPT-4 Turbo: $0.01/1K prompt tokens, $0.03/1K completion tokens

---

**Status**: Ready for Worker08  
**Created**: 2025-11-24  
**Owner**: Worker01  
**Reviewer**: Worker10
