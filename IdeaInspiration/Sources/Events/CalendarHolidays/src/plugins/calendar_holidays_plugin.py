"""Calendar holidays plugin using Python holidays library."""

import holidays
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from . import SourcePlugin


class CalendarHolidaysPlugin(SourcePlugin):
    """Plugin for scraping holidays using Python holidays library."""
    
    def __init__(self, config):
        """Initialize calendar holidays plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "calendar_holidays"
    
    def scrape(
        self,
        country: Optional[str] = None,
        year: Optional[int] = None,
        years: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Scrape holidays from Python holidays library.
        
        Args:
            country: Country code (e.g., 'US', 'GB', 'CA')
            year: Single year to get holidays for
            years: List of years to get holidays for
            
        Returns:
            List of holiday dictionaries
        """
        events = []
        
        # Use config values if not provided
        if country is None:
            country = getattr(self.config, 'default_country', 'US')
        
        # Determine years to fetch
        if years is None:
            if year is None:
                year = int(getattr(self.config, 'default_year', datetime.now().year))
            years = [year]
        
        # Get holidays for the country
        try:
            for yr in years:
                country_holidays = holidays.country_holidays(country, years=yr)
                
                for date, name in sorted(country_holidays.items()):
                    # Build holiday data
                    holiday_data = {
                        'id': f"{country}_{name.replace(' ', '_')}_{date.isoformat()}",
                        'name': name,
                        'date': date.isoformat(),
                        'type': 'holiday',
                        'country': country,
                        'recurring': True,
                        'recurrence_pattern': 'annual',
                        'scope': self._determine_scope(country, name),
                        'importance': self._determine_importance(name),
                        'audience_size_estimate': self._estimate_audience(country, name),
                        'description': f"{name} - {country} holiday"
                    }
                    
                    events.append(holiday_data)
        
        except (KeyError, AttributeError) as e:
            print(f"Error fetching holidays for country '{country}': Invalid country code or API error")
            print(f"Try using a valid ISO 3166-1 alpha-2 country code (e.g., US, GB, CA, etc.)")
        
        return events
    
    def _determine_scope(self, country: str, name: str) -> str:
        """Determine the scope of a holiday.
        
        Args:
            country: Country code
            name: Holiday name
            
        Returns:
            Scope: global, national, regional, or local
        """
        # Global holidays
        global_holidays = [
            'New Year', 'Christmas', 'New Year\'s Day', 'Christmas Day'
        ]
        
        for gh in global_holidays:
            if gh.lower() in name.lower():
                return 'global'
        
        # All others are considered national by default
        return 'national'
    
    def _determine_importance(self, name: str) -> str:
        """Determine the importance of a holiday.
        
        Args:
            name: Holiday name
            
        Returns:
            Importance: major, moderate, or minor
        """
        # Major holidays
        major = [
            'Christmas', 'New Year', 'Thanksgiving', 'Easter',
            'Independence Day', 'Labour Day', 'Memorial Day'
        ]
        
        # Moderate holidays
        moderate = [
            'Valentine', 'Halloween', 'Mother', 'Father',
            'Veterans', 'Martin Luther King'
        ]
        
        name_lower = name.lower()
        
        for maj in major:
            if maj.lower() in name_lower:
                return 'major'
        
        for mod in moderate:
            if mod.lower() in name_lower:
                return 'moderate'
        
        return 'minor'
    
    def _estimate_audience(self, country: str, name: str) -> int:
        """Estimate audience size for a holiday.
        
        Args:
            country: Country code
            name: Holiday name
            
        Returns:
            Estimated audience size
        """
        # Population estimates for major countries
        populations = {
            'US': 330_000_000,
            'GB': 67_000_000,
            'CA': 38_000_000,
            'AU': 26_000_000,
            'IN': 1_400_000_000,
            'DE': 83_000_000,
            'FR': 67_000_000,
            'IT': 60_000_000,
            'ES': 47_000_000,
            'MX': 128_000_000,
            'BR': 212_000_000,
            'JP': 125_000_000,
            'CN': 1_400_000_000,
        }
        
        # Get base population
        base_pop = populations.get(country.upper(), 50_000_000)
        
        # Apply multiplier based on importance
        scope = self._determine_scope(country, name)
        importance = self._determine_importance(name)
        
        # Scope multiplier
        if scope == 'global':
            base_pop = 2_000_000_000  # Assume 2 billion for global holidays
        
        # Importance multiplier
        importance_mult = {
            'major': 0.9,
            'moderate': 0.5,
            'minor': 0.2
        }
        
        mult = importance_mult.get(importance, 0.3)
        
        return int(base_pop * mult)
