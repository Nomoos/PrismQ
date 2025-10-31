"""Event processor for transforming holiday data to unified format."""

from typing import Dict, Any, Optional
from datetime import datetime


class EventProcessor:
    """Processes holiday data into unified event signal format."""
    
    @staticmethod
    def process_holiday(holiday_data: Dict[str, Any], source: str = "calendar_holidays") -> Dict[str, Any]:
        """Process holiday data into unified event format.
        
        Args:
            holiday_data: Raw holiday data from source
            source: Source identifier
            
        Returns:
            Unified event signal dictionary
        """
        # Extract basic event info
        event_name = holiday_data.get('name', 'Unknown Holiday')
        event_date = holiday_data.get('date', '')
        event_type = holiday_data.get('type', 'holiday')
        
        # Determine if recurring (most holidays recur annually)
        recurring = holiday_data.get('recurring', True)
        recurrence_pattern = holiday_data.get('recurrence_pattern', 'annual' if recurring else None)
        
        # Extract significance data
        scope = holiday_data.get('scope', 'national')
        importance = holiday_data.get('importance', 'moderate')
        audience_size = holiday_data.get('audience_size_estimate', 0)
        
        # Calculate content window
        pre_event_days = EventProcessor._calculate_pre_event_days(importance, scope)
        post_event_days = EventProcessor._calculate_post_event_days(importance, scope)
        
        # Build metadata
        metadata = {
            'country': holiday_data.get('country', 'US'),
            'description': holiday_data.get('description', ''),
            'locations': holiday_data.get('locations', []),
            'states': holiday_data.get('states', []),
            'type': holiday_data.get('type', 'Public'),
        }
        
        # Add any additional fields
        for key in ['primary_type', 'canonical_url', 'urlid', 'locations']:
            if key in holiday_data:
                metadata[key] = holiday_data[key]
        
        # Build universal metrics placeholder (will be calculated later)
        universal_metrics = {
            'significance_score': EventProcessor._calculate_significance(importance, scope),
            'content_opportunity': EventProcessor._calculate_content_opportunity(importance, scope),
            'audience_interest': EventProcessor._calculate_audience_interest(scope, recurring)
        }
        
        # Build unified event signal
        event_signal = {
            'source': source,
            'source_id': holiday_data.get('id', f"{event_name}_{event_date}"),
            'event': {
                'name': event_name,
                'type': event_type,
                'date': event_date,
                'recurring': recurring,
                'recurrence_pattern': recurrence_pattern
            },
            'significance': {
                'scope': scope,
                'importance': importance,
                'audience_size_estimate': audience_size
            },
            'content_window': {
                'pre_event_days': pre_event_days,
                'post_event_days': post_event_days,
                'peak_day': event_date
            },
            'metadata': metadata,
            'universal_metrics': universal_metrics
        }
        
        return event_signal
    
    @staticmethod
    def _calculate_pre_event_days(importance: str, scope: str) -> int:
        """Calculate pre-event content window.
        
        Args:
            importance: Event importance level
            scope: Geographic scope
            
        Returns:
            Number of days before event to start coverage
        """
        base_days = {
            'major': 21,
            'moderate': 14,
            'minor': 7
        }
        
        scope_multiplier = {
            'global': 1.5,
            'national': 1.0,
            'regional': 0.7,
            'local': 0.5
        }
        
        days = base_days.get(importance, 14)
        multiplier = scope_multiplier.get(scope, 1.0)
        
        return int(days * multiplier)
    
    @staticmethod
    def _calculate_post_event_days(importance: str, scope: str) -> int:
        """Calculate post-event content window.
        
        Args:
            importance: Event importance level
            scope: Geographic scope
            
        Returns:
            Number of days after event to continue coverage
        """
        # Post-event is typically shorter than pre-event
        base_days = {
            'major': 14,
            'moderate': 7,
            'minor': 3
        }
        
        scope_multiplier = {
            'global': 1.5,
            'national': 1.0,
            'regional': 0.7,
            'local': 0.5
        }
        
        days = base_days.get(importance, 7)
        multiplier = scope_multiplier.get(scope, 1.0)
        
        return int(days * multiplier)
    
    @staticmethod
    def _calculate_significance(importance: str, scope: str) -> float:
        """Calculate significance score.
        
        Args:
            importance: Event importance level
            scope: Geographic scope
            
        Returns:
            Significance score (0-10)
        """
        scope_scores = {
            'global': 10.0,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        importance_multiplier = {
            'major': 1.0,
            'moderate': 0.7,
            'minor': 0.4
        }
        
        base = scope_scores.get(scope, 5.0)
        mult = importance_multiplier.get(importance, 0.7)
        
        return round(base * mult, 2)
    
    @staticmethod
    def _calculate_content_opportunity(importance: str, scope: str) -> float:
        """Calculate content opportunity score.
        
        Args:
            importance: Event importance level
            scope: Geographic scope
            
        Returns:
            Content opportunity score (0-10)
        """
        # Content opportunity is slightly lower than significance
        sig = EventProcessor._calculate_significance(importance, scope)
        return round(sig * 0.9, 2)
    
    @staticmethod
    def _calculate_audience_interest(scope: str, recurring: bool) -> float:
        """Calculate audience interest score.
        
        Args:
            scope: Geographic scope
            recurring: Whether event recurs
            
        Returns:
            Audience interest score (0-10)
        """
        scope_scores = {
            'global': 9.0,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        base = scope_scores.get(scope, 5.0)
        
        # Recurring events typically have more interest
        if recurring:
            base *= 1.2
        
        return round(min(10.0, base), 2)
