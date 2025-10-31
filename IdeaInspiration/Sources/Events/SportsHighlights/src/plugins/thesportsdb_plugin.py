"""TheSportsDB sports highlights plugin."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from . import SourcePlugin


class TheSportsDBPlugin(SourcePlugin):
    """Plugin for scraping sports events using TheSportsDB API."""
    
    API_BASE_URL = "https://www.thesportsdb.com/api/v1/json"
    
    def __init__(self, config):
        """Initialize TheSportsDB plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.api_key = getattr(config, 'thesportsdb_api_key', '3')  # 3 is test key
        self.api_url = f"{self.API_BASE_URL}/{self.api_key}"
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "thesportsdb"
    
    def scrape(
        self,
        league: Optional[str] = None,
        season: Optional[str] = None,
        date: Optional[str] = None,
        next_events: bool = True,
        max_events: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Scrape sports events from TheSportsDB.
        
        Args:
            league: League name or ID
            season: Season (e.g., "2024-2025")
            date: Specific date to get events for (YYYY-MM-DD)
            next_events: Get next upcoming events instead of past
            max_events: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        # Use config values if not provided
        if max_events is None:
            max_events = getattr(self.config, 'max_events', 50)
        
        # If league not provided, use default or search for popular leagues
        if league is None:
            league = getattr(self.config, 'default_league', None)
        
        # Get league ID if league name provided
        league_id = self._get_league_id(league) if league else None
        
        if league_id and next_events:
            # Get next events for league
            league_events = self._get_next_league_events(league_id, max_events)
            events.extend(league_events)
        elif league_id and season:
            # Get season events
            season_events = self._get_season_events(league_id, season, max_events)
            events.extend(season_events)
        elif date:
            # Get events on specific date
            date_events = self._get_events_by_date(date, max_events)
            events.extend(date_events)
        else:
            # Default: Get next events for multiple popular leagues
            popular_leagues = self._get_popular_leagues()
            for league_name in popular_leagues[:5]:  # Top 5 leagues
                lid = self._get_league_id(league_name)
                if lid:
                    league_events = self._get_next_league_events(lid, max_events // 5)
                    events.extend(league_events)
        
        return events[:max_events]
    
    def _get_league_id(self, league_name: str) -> Optional[str]:
        """Get league ID from league name.
        
        Args:
            league_name: Name of the league
            
        Returns:
            League ID or None
        """
        try:
            # Search for league
            response = requests.get(
                f"{self.api_url}/search_all_leagues.php",
                params={'s': 'Soccer'},  # Search in Soccer first
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'countrys' in data:
                for league in data['countrys']:
                    if league and league.get('strLeague', '').lower() == league_name.lower():
                        return league.get('idLeague')
            
            # Try alternative lookup
            response = requests.get(
                f"{self.api_url}/search_all_leagues.php",
                params={'c': league_name},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'countrys' in data and data['countrys']:
                return data['countrys'][0].get('idLeague')
                
        except Exception as e:
            print(f"Error getting league ID for '{league_name}': API lookup failed")
        
        return None
    
    def _get_next_league_events(self, league_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Get next events for a league.
        
        Args:
            league_id: League ID
            limit: Maximum number of events
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            response = requests.get(
                f"{self.api_url}/eventsnextleague.php",
                params={'id': league_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'events' in data and data['events']:
                for event in data['events'][:limit]:
                    processed_event = self._process_event(event)
                    if processed_event:
                        events.append(processed_event)
        
        except Exception as e:
            print(f"Error getting next events for league: API request failed")
        
        return events
    
    def _get_season_events(
        self,
        league_id: str,
        season: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get events for a specific season.
        
        Args:
            league_id: League ID
            season: Season identifier
            limit: Maximum number of events
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            response = requests.get(
                f"{self.api_url}/eventsseason.php",
                params={'id': league_id, 's': season},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'events' in data and data['events']:
                for event in data['events'][:limit]:
                    processed_event = self._process_event(event)
                    if processed_event:
                        events.append(processed_event)
        
        except Exception as e:
            print(f"Error getting season events: API request failed")
        
        return events
    
    def _get_events_by_date(self, date: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events on a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            limit: Maximum number of events
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            response = requests.get(
                f"{self.api_url}/eventsday.php",
                params={'d': date, 's': 'Soccer'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data and 'events' in data and data['events']:
                for event in data['events'][:limit]:
                    processed_event = self._process_event(event)
                    if processed_event:
                        events.append(processed_event)
        
        except Exception as e:
            print(f"Error getting events for date {date}: API request failed")
        
        return events
    
    def _process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process raw event data from API.
        
        Args:
            event: Raw event data from TheSportsDB
            
        Returns:
            Processed event dictionary or None
        """
        if not event:
            return None
        
        # Determine importance based on league/round
        importance = 'regular'
        event_round = event.get('intRound', '')
        if 'final' in str(event_round).lower() or 'championship' in str(event.get('strEvent', '')).lower():
            importance = 'championship'
        elif 'semi' in str(event_round).lower() or 'quarter' in str(event_round).lower():
            importance = 'playoff'
        
        # Determine scope
        scope = 'national'
        league = event.get('strLeague', '')
        if any(x in league.lower() for x in ['world', 'champions', 'europa', 'international']):
            scope = 'international'
        
        # Build event data
        event_data = {
            'id': event.get('idEvent'),
            'name': event.get('strEvent', ''),
            'date': event.get('dateEvent', ''),
            'time': event.get('strTime', ''),
            'type': 'sports',
            'sport': event.get('strSport', ''),
            'league': league,
            'season': event.get('strSeason', ''),
            'home_team': event.get('strHomeTeam', ''),
            'away_team': event.get('strAwayTeam', ''),
            'venue': event.get('strVenue', ''),
            'city': event.get('strCity', ''),
            'country': event.get('strCountry', ''),
            'scope': scope,
            'importance': importance,
            'recurring': False,
            'audience_size_estimate': self._estimate_viewership(scope, importance, league),
        }
        
        # Add scores if available
        if event.get('intHomeScore') is not None:
            event_data['home_score'] = event.get('intHomeScore')
            event_data['away_score'] = event.get('intAwayScore')
        
        return event_data
    
    def _get_popular_leagues(self) -> List[str]:
        """Get list of popular leagues.
        
        Returns:
            List of league names
        """
        return [
            "English Premier League",
            "Spanish La Liga",
            "German Bundesliga",
            "Italian Serie A",
            "French Ligue 1",
            "UEFA Champions League",
            "NBA",
            "NFL",
            "MLB",
            "NHL"
        ]
    
    def _estimate_viewership(self, scope: str, importance: str, league: str) -> int:
        """Estimate event viewership.
        
        Args:
            scope: Geographic scope
            importance: Event importance
            league: League name
            
        Returns:
            Estimated viewership
        """
        base_viewership = {
            'international': 500_000_000,
            'national': 50_000_000,
            'regional': 5_000_000,
            'local': 500_000
        }
        
        importance_mult = {
            'championship': 3.0,
            'playoff': 2.0,
            'major': 1.5,
            'regular': 1.0,
            'moderate': 1.0,
            'minor': 0.5
        }
        
        base = base_viewership.get(scope, 10_000_000)
        mult = importance_mult.get(importance, 1.0)
        
        # Boost for major leagues
        if any(x in league.lower() for x in ['champions', 'world cup', 'premier', 'nba', 'nfl']):
            mult *= 2
        
        return int(base * mult)
