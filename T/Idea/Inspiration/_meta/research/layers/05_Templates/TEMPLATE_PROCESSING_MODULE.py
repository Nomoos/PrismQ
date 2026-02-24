"""
Template for creating a new Processing Module.

Location: {ModuleName}/src/

Processing modules enrich IdeaInspiration objects with additional data.
Examples: Classification, Scoring, Sentiment Analysis, etc.

Usage:
1. Copy this template
2. Rename to {module_name}.py
3. Replace all {PLACEHOLDERS}
4. Implement the processing logic
5. Write tests in tests/test_{module_name}.py

Principles:
- Stateless processing (no side effects on other modules)
- Idempotent (can run multiple times safely)
- Depends only on Model and EnvLoad layers
- Returns enriched IdeaInspiration (immutable pattern)
"""

import logging
from typing import Any, Dict, Optional

from Model import IdeaInspiration
from src import Config


class {ModuleName}Processor:
    """{Purpose} processor for IdeaInspiration objects.
    
    This processor {what it does} by {how it does it}.
    It follows the Single Responsibility Principle by focusing
    solely on {specific responsibility}.
    
    Design Principles:
    - Single Responsibility: Only handles {responsibility}
    - Dependency Inversion: Depends on injected Config
    - Stateless: No side effects, thread-safe
    - Idempotent: Can be run multiple times safely
    
    Attributes:
        config: Configuration object
        logger: Logger instance
        {other_attributes}: Description
    
    Example:
        >>> config = Config()
        >>> processor = {ModuleName}Processor(config)
        >>> enriched = processor.process(idea)
        >>> assert enriched.{new_field} is not None
    """
    
    def __init__(self, config: Config):
        """Initialize processor with configuration.
        
        Args:
            config: Configuration object with processor settings
        
        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize processor-specific attributes from config
        self.{setting_name} = config.{setting_key}
        
        # Validate configuration
        self._validate_config()
    
    def process(self, idea: IdeaInspiration) -> IdeaInspiration:
        """Process an idea and return enriched version.
        
        This method is the main entry point for processing.
        It takes an IdeaInspiration object, performs {processing},
        and returns a new IdeaInspiration with additional fields.
        
        Args:
            idea: The IdeaInspiration object to process
        
        Returns:
            New IdeaInspiration object with enriched data:
            - {new_field_1}: Description
            - {new_field_2}: Description
        
        Raises:
            ValueError: If idea data is invalid
            ProcessingError: If processing fails
        
        Example:
            >>> processor = {ModuleName}Processor(config)
            >>> idea = IdeaInspiration(title="Example", ...)
            >>> enriched = processor.process(idea)
            >>> print(enriched.{new_field})
        
        Note:
            This method is idempotent - calling it multiple times
            on the same idea will produce the same result.
        """
        try:
            # Validate input
            self._validate_input(idea)
            
            # Perform processing
            results = self._do_processing(idea)
            
            # Create enriched IdeaInspiration (immutable pattern)
            enriched = IdeaInspiration(
                **idea.__dict__,  # Copy existing fields
                {new_field_1}=results['{new_field_1}'],
                {new_field_2}=results['{new_field_2}'],
            )
            
            self.logger.debug(f"Processed idea {idea.id}")
            return enriched
            
        except Exception as e:
            self.logger.error(f"Failed to process idea {idea.id}: {e}")
            raise
    
    def batch_process(self, ideas: list[IdeaInspiration]) -> list[IdeaInspiration]:
        """Process multiple ideas efficiently.
        
        For processors that can benefit from batch processing
        (e.g., ML models that support batching), implement this method.
        Otherwise, it defaults to processing one-by-one.
        
        Args:
            ideas: List of IdeaInspiration objects to process
        
        Returns:
            List of enriched IdeaInspiration objects
        
        Example:
            >>> processor = {ModuleName}Processor(config)
            >>> ideas = [idea1, idea2, idea3]
            >>> enriched_ideas = processor.batch_process(ideas)
        """
        # Default implementation: process one-by-one
        # Override this if you can benefit from batching
        return [self.process(idea) for idea in ideas]
    
    # Private helper methods (internal implementation)
    
    def _validate_config(self) -> None:
        """Validate configuration.
        
        Raises:
            ValueError: If required configuration is missing
        """
        # TODO: Implement validation
        # Example:
        # if not self.{required_setting}:
        #     raise ValueError("{Setting} is required")
        pass
    
    def _validate_input(self, idea: IdeaInspiration) -> None:
        """Validate input idea.
        
        Args:
            idea: IdeaInspiration to validate
        
        Raises:
            ValueError: If idea data is invalid
        """
        # TODO: Implement validation
        # Example:
        # if not idea.title:
        #     raise ValueError("Idea title is required")
        # if len(idea.title) > 1000:
        #     raise ValueError("Idea title too long")
        pass
    
    def _do_processing(self, idea: IdeaInspiration) -> Dict[str, Any]:
        """Perform the actual processing logic.
        
        This is where the main processing happens. Keep this method
        focused and extract helper methods as needed.
        
        Args:
            idea: IdeaInspiration to process
        
        Returns:
            Dictionary with processing results:
            {
                '{new_field_1}': value,
                '{new_field_2}': value,
            }
        """
        # TODO: Implement processing logic
        # Example:
        # text = self._extract_text(idea)
        # features = self._extract_features(text)
        # result = self._calculate_result(features)
        # 
        # return {
        #     '{new_field_1}': result.field1,
        #     '{new_field_2}': result.field2,
        # }
        pass
    
    def _extract_text(self, idea: IdeaInspiration) -> str:
        """Extract text content from idea for processing.
        
        Args:
            idea: IdeaInspiration object
        
        Returns:
            Combined text from title and description
        """
        # Example implementation
        text_parts = []
        if idea.title:
            text_parts.append(idea.title)
        if idea.description:
            text_parts.append(idea.description)
        return " ".join(text_parts)


# Alternative: Protocol-based approach for more flexibility

from typing import Protocol


class IdeaProcessor(Protocol):
    """Protocol defining the interface for idea processors.
    
    This allows for flexible implementations while maintaining
    a consistent interface (Interface Segregation Principle).
    """
    
    def process(self, idea: IdeaInspiration) -> IdeaInspiration:
        """Process an idea and return enriched version."""
        ...


# Testing Template
"""
Create tests/test_{module_name}.py:

import pytest
from unittest.mock import Mock, patch
from {module}.{module_name} import {ModuleName}Processor
from Model import IdeaInspiration
from src import Config


class Test{ModuleName}Processor:
    '''Tests for {ModuleName}Processor.'''
    
    @pytest.fixture
    def config(self):
        '''Provide test configuration.'''
        config = Mock(spec=Config)
        config.{setting_key} = 'test_value'
        return config
    
    @pytest.fixture
    def processor(self, config):
        '''Provide processor instance.'''
        return {ModuleName}Processor(config)
    
    @pytest.fixture
    def sample_idea(self):
        '''Provide sample IdeaInspiration.'''
        return IdeaInspiration(
            id='test-1',
            source='test',
            platform='test',
            title='Sample Title',
            description='Sample description',
        )
    
    def test_process_returns_enriched_idea(self, processor, sample_idea):
        '''process() returns IdeaInspiration with new fields.'''
        # Act
        enriched = processor.process(sample_idea)
        
        # Assert
        assert isinstance(enriched, IdeaInspiration)
        assert enriched.{new_field} is not None
        # Original fields preserved
        assert enriched.id == sample_idea.id
        assert enriched.title == sample_idea.title
    
    def test_process_handles_empty_description(self, processor):
        '''process() handles idea with empty description.'''
        # Arrange
        idea = IdeaInspiration(
            id='test-2',
            source='test',
            platform='test',
            title='Title Only',
            description=None,
        )
        
        # Act
        enriched = processor.process(idea)
        
        # Assert
        assert enriched.{new_field} is not None
    
    def test_process_raises_on_empty_title(self, processor):
        '''process() raises ValueError for empty title.'''
        # Arrange
        idea = IdeaInspiration(
            id='test-3',
            source='test',
            platform='test',
            title='',
            description='Has description',
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="title"):
            processor.process(idea)
    
    def test_process_is_idempotent(self, processor, sample_idea):
        '''process() produces same result when called multiple times.'''
        # Act
        result1 = processor.process(sample_idea)
        result2 = processor.process(sample_idea)
        
        # Assert
        assert result1.{new_field} == result2.{new_field}
    
    def test_batch_process_handles_multiple_ideas(self, processor, sample_idea):
        '''batch_process() processes multiple ideas.'''
        # Arrange
        ideas = [sample_idea] * 3
        
        # Act
        enriched = processor.batch_process(ideas)
        
        # Assert
        assert len(enriched) == 3
        assert all(isinstance(idea, IdeaInspiration) for idea in enriched)
        assert all(idea.{new_field} is not None for idea in enriched)
    
    def test_validate_config_raises_on_missing_setting(self):
        '''Processor raises ValueError if required config missing.'''
        # Arrange
        config = Mock(spec=Config)
        config.{setting_key} = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="{setting}"):
            {ModuleName}Processor(config)
"""


# Example: Specific Processing Module Types

class Classifier({ModuleName}Processor):
    """Example: Classification processor.
    
    Classifies ideas into predefined categories.
    """
    
    def _do_processing(self, idea: IdeaInspiration) -> Dict[str, Any]:
        """Classify idea into categories."""
        text = self._extract_text(idea)
        categories = self._classify_text(text)
        confidence = self._calculate_confidence(text, categories)
        
        return {
            'categories': categories,
            'classification_confidence': confidence,
        }
    
    def _classify_text(self, text: str) -> list[str]:
        """Classify text into categories."""
        # TODO: Implement classification logic
        pass


class Scorer({ModuleName}Processor):
    """Example: Scoring processor.
    
    Calculates quality and engagement scores.
    """
    
    def _do_processing(self, idea: IdeaInspiration) -> Dict[str, Any]:
        """Calculate scores for idea."""
        quality = self._calculate_quality_score(idea)
        engagement = self._calculate_engagement_score(idea)
        
        return {
            'quality_score': quality,
            'engagement_score': engagement,
            'overall_score': (quality + engagement) / 2,
        }
    
    def _calculate_quality_score(self, idea: IdeaInspiration) -> float:
        """Calculate quality score (0-100)."""
        # TODO: Implement scoring logic
        pass
