"""Event processor for transforming entertainment release data to unified format."""

from typing import Dict, Any


class EventProcessor:
    """Processes entertainment release data into unified event signal format."""
    
    @staticmethod
    def process_release(release_data: Dict[str, Any], source: str = "entertainment_releases") -> Dict[str, Any]:
        """Process entertainment release data into unified event format."""
        event_name = release_data.get('name', release_data.get('title', 'Unknown Release'))
        event_date = release_data.get('date', release_data.get('release_date', ''))
        media_type = release_data.get('media_type', 'movie')
        
        event_type = f"{media_type}_release"
        recurring = False
        scope = release_data.get('scope', 'limited')
        importance = release_data.get('importance', 'moderate')
        
        pre_event_days = EventProcessor._calculate_pre_event_days(importance, scope)
        post_event_days = EventProcessor._calculate_post_event_days(importance, scope)
        
        metadata = {
            'media_type': media_type,
            'genre': release_data.get('genre', []),
            'director': release_data.get('director', ''),
            'cast': release_data.get('cast', []),
            'studio': release_data.get('studio', ''),
            'runtime': release_data.get('runtime'),
            'rating': release_data.get('rating', ''),
        }
        
        universal_metrics = {
            'significance_score': EventProcessor._calculate_significance(importance, scope),
            'content_opportunity': EventProcessor._calculate_content_opportunity(importance, scope),
            'audience_interest': EventProcessor._calculate_audience_interest(scope, importance)
        }
        
        return {
            'source': source,
            'source_id': release_data.get('id', f"{event_name}_{event_date}"),
            'event': {
                'name': event_name,
                'type': event_type,
                'date': event_date,
                'recurring': recurring,
                'recurrence_pattern': None
            },
            'significance': {
                'scope': scope,
                'importance': importance,
                'audience_size_estimate': release_data.get('audience_size_estimate', 0)
            },
            'content_window': {
                'pre_event_days': pre_event_days,
                'post_event_days': post_event_days,
                'peak_day': event_date
            },
            'metadata': metadata,
            'universal_metrics': universal_metrics
        }
    
    @staticmethod
    def _calculate_pre_event_days(importance: str, scope: str) -> int:
        base_days = {'blockbuster': 30, 'major': 14, 'moderate': 7, 'indie': 3}
        scope_mult = {'worldwide': 1.5, 'limited': 1.0, 'exclusive': 0.7}
        return int(base_days.get(importance, 7) * scope_mult.get(scope, 1.0))
    
    @staticmethod
    def _calculate_post_event_days(importance: str, scope: str) -> int:
        base_days = {'blockbuster': 14, 'major': 7, 'moderate': 3, 'indie': 1}
        scope_mult = {'worldwide': 1.5, 'limited': 1.0, 'exclusive': 0.7}
        return int(base_days.get(importance, 3) * scope_mult.get(scope, 1.0))
    
    @staticmethod
    def _calculate_significance(importance: str, scope: str) -> float:
        scope_scores = {'worldwide': 10.0, 'limited': 6.0, 'exclusive': 4.0}
        importance_mult = {'blockbuster': 1.3, 'major': 1.0, 'moderate': 0.7, 'indie': 0.4}
        return round(min(10.0, scope_scores.get(scope, 6.0) * importance_mult.get(importance, 0.7)), 2)
    
    @staticmethod
    def _calculate_content_opportunity(importance: str, scope: str) -> float:
        return round(EventProcessor._calculate_significance(importance, scope) * 0.88, 2)
    
    @staticmethod
    def _calculate_audience_interest(scope: str, importance: str) -> float:
        scope_scores = {'worldwide': 9.0, 'limited': 6.0, 'exclusive': 4.0}
        base = scope_scores.get(scope, 6.0)
        if importance == 'blockbuster':
            base *= 1.3
        return round(min(10.0, base), 2)
