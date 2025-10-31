"""Event processor for transforming sports data to unified format."""

from typing import Dict, Any, Optional
from datetime import datetime


class EventProcessor:
    """Processes sports event data into unified event signal format."""
    
    @staticmethod
    def process_sports_event(event_data: Dict[str, Any], source: str = "sports_highlights") -> Dict[str, Any]:
        """Process sports event data into unified event format.
        
        Args:
            event_data: Raw sports event data from source
            source: Source identifier
            
        Returns:
            Unified event signal dictionary
        """
        # Extract basic event info
        event_name = event_data.get('name', event_data.get('strEvent', 'Unknown Event'))
        event_date = event_data.get('date', event_data.get('dateEvent', ''))
        event_type = event_data.get('type', 'sports')
        
        # Extract teams/participants
        home_team = event_data.get('home_team', event_data.get('strHomeTeam', ''))
        away_team = event_data.get('away_team', event_data.get('strAwayTeam', ''))
        participants = [home_team, away_team] if home_team and away_team else []
        
        # Determine if recurring (most sports games don't recur exactly)
        recurring = event_data.get('recurring', False)
        recurrence_pattern = event_data.get('recurrence_pattern', None)
        
        # Extract significance data
        scope = event_data.get('scope', 'national')
        importance = event_data.get('importance', 'regular')
        audience_size = event_data.get('audience_size_estimate', 0)
        
        # Calculate content window
        pre_event_days = EventProcessor._calculate_pre_event_days(importance, scope)
        post_event_days = EventProcessor._calculate_post_event_days(importance, scope)
        
        # Build metadata
        metadata = {
            'sport': event_data.get('sport', event_data.get('strSport', '')),
            'league': event_data.get('league', event_data.get('strLeague', '')),
            'season': event_data.get('season', event_data.get('strSeason', '')),
            'round': event_data.get('round', event_data.get('intRound', '')),
            'venue': event_data.get('venue', event_data.get('strVenue', '')),
            'city': event_data.get('city', event_data.get('strCity', '')),
            'country': event_data.get('country', event_data.get('strCountry', '')),
        }
        
        # Add scores if available (for completed events)
        if 'home_score' in event_data or 'intHomeScore' in event_data:
            metadata['home_score'] = event_data.get('home_score', event_data.get('intHomeScore'))
            metadata['away_score'] = event_data.get('away_score', event_data.get('intAwayScore'))
        
        # Build universal metrics placeholder
        universal_metrics = {
            'significance_score': EventProcessor._calculate_significance(importance, scope),
            'content_opportunity': EventProcessor._calculate_content_opportunity(importance, scope),
            'audience_interest': EventProcessor._calculate_audience_interest(scope, importance)
        }
        
        # Build unified event signal
        event_signal = {
            'source': source,
            'source_id': event_data.get('id', event_data.get('idEvent', f"{event_name}_{event_date}")),
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
        
        # Add participants if available
        if participants:
            event_signal['metadata']['participants'] = participants
        
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
            'championship': 14,
            'playoff': 7,
            'major': 7,
            'regular': 3,
            'moderate': 3,
            'minor': 1
        }
        
        scope_multiplier = {
            'global': 1.5,
            'international': 1.3,
            'national': 1.0,
            'regional': 0.7,
            'local': 0.5
        }
        
        days = base_days.get(importance, 3)
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
        # Post-event coverage for sports is typically shorter
        base_days = {
            'championship': 7,
            'playoff': 3,
            'major': 3,
            'regular': 1,
            'moderate': 1,
            'minor': 1
        }
        
        scope_multiplier = {
            'global': 1.5,
            'international': 1.3,
            'national': 1.0,
            'regional': 0.7,
            'local': 0.5
        }
        
        days = base_days.get(importance, 1)
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
            'international': 9.0,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        importance_multiplier = {
            'championship': 1.2,
            'playoff': 1.0,
            'major': 1.0,
            'regular': 0.7,
            'moderate': 0.7,
            'minor': 0.4
        }
        
        base = scope_scores.get(scope, 5.0)
        mult = importance_multiplier.get(importance, 0.7)
        
        return round(min(10.0, base * mult), 2)
    
    @staticmethod
    def _calculate_content_opportunity(importance: str, scope: str) -> float:
        """Calculate content opportunity score.
        
        Args:
            importance: Event importance level
            scope: Geographic scope
            
        Returns:
            Content opportunity score (0-10)
        """
        sig = EventProcessor._calculate_significance(importance, scope)
        return round(sig * 0.85, 2)
    
    @staticmethod
    def _calculate_audience_interest(scope: str, importance: str) -> float:
        """Calculate audience interest score.
        
        Args:
            scope: Geographic scope
            importance: Event importance level
            
        Returns:
            Audience interest score (0-10)
        """
        scope_scores = {
            'global': 9.5,
            'international': 8.5,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        base = scope_scores.get(scope, 5.0)
        
        # Championship and playoff games have more interest
        if importance in ['championship', 'playoff']:
            base *= 1.3
        
        return round(min(10.0, base), 2)
