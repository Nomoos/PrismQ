"""SocialChallenge plugin for scraping challenge signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


class SocialChallengePlugin(SignalPlugin):
    """Plugin for scraping viral social media challenge signals."""
    
    def __init__(self, config):
        """Initialize SocialChallenge plugin."""
        super().__init__(config)
        self.api = None
        print("SocialChallenge initialized in stub mode")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "social_challenge"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape challenge signals from various platforms.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of challenges to fetch
                - platform: Specific platform to track (tiktok, instagram, etc.)
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'social_challenge_max_results', 25)
        limit = kwargs.get('limit', max_results)
        platform = kwargs.get('platform', 'all')
        
        try:
            print("Running in stub mode - returning sample challenge data")
            signals = self._get_sample_challenges(limit, platform)
            print(f"Successfully scraped {len(signals)} challenge signals from SocialChallenge")
            
        except Exception as e:
            print(f"Error scraping social challenges: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _get_sample_challenges(self, limit: int = 10, platform: str = 'all') -> List[Dict[str, Any]]:
        """
        Generate sample challenge data for testing.
        
        Args:
            limit: Number of challenges to generate
            platform: Platform filter
            
        Returns:
            List of signal dictionaries
        """
        challenges = [
            {
                'name': '#DanceChallenge2024',
                'description': 'Viral dance challenge with trending audio',
                'platform': 'tiktok',
                'participants': 5000000,
                'hashtag': '#DanceChallenge2024',
                'origin_date': '2024-10-15',
                'category': 'dance'
            },
            {
                'name': '#BookTok Reading Challenge',
                'description': 'Monthly reading challenge for book lovers',
                'platform': 'tiktok',
                'participants': 2500000,
                'hashtag': '#BookTokChallenge',
                'origin_date': '2024-10-20',
                'category': 'education'
            },
            {
                'name': '#ReelsChallenge',
                'description': 'Instagram Reels creative challenge',
                'platform': 'instagram',
                'participants': 3000000,
                'hashtag': '#ReelsChallenge',
                'origin_date': '2024-10-18',
                'category': 'creative'
            },
            {
                'name': '#FitnessChallenge30Days',
                'description': '30-day fitness transformation challenge',
                'platform': 'instagram',
                'participants': 1800000,
                'hashtag': '#FitnessChallenge',
                'origin_date': '2024-10-01',
                'category': 'fitness'
            },
            {
                'name': '#CookingChallenge',
                'description': 'Recipe challenge with mystery ingredients',
                'platform': 'youtube',
                'participants': 1200000,
                'hashtag': '#CookingChallenge',
                'origin_date': '2024-10-22',
                'category': 'food'
            },
            {
                'name': '#DIYChallenge',
                'description': 'Creative DIY project challenge',
                'platform': 'tiktok',
                'participants': 2200000,
                'hashtag': '#DIYChallenge',
                'origin_date': '2024-10-12',
                'category': 'creative'
            },
            {
                'name': '#PhotoChallenge',
                'description': 'Daily photography challenge',
                'platform': 'instagram',
                'participants': 1500000,
                'hashtag': '#PhotoChallenge',
                'origin_date': '2024-10-10',
                'category': 'photography'
            },
            {
                'name': '#ChallengeAccepted',
                'description': 'General viral challenge tag',
                'platform': 'all',
                'participants': 10000000,
                'hashtag': '#ChallengeAccepted',
                'origin_date': '2024-09-01',
                'category': 'viral'
            },
            {
                'name': '#MakeupChallenge',
                'description': 'Beauty transformation challenge',
                'platform': 'tiktok',
                'participants': 3500000,
                'hashtag': '#MakeupChallenge',
                'origin_date': '2024-10-17',
                'category': 'beauty'
            },
            {
                'name': '#LanguageLearningChallenge',
                'description': 'Learn a new language in 30 days',
                'platform': 'youtube',
                'participants': 800000,
                'hashtag': '#LanguageChallenge',
                'origin_date': '2024-10-05',
                'category': 'education'
            }
        ]
        
        # Filter by platform if specified
        if platform != 'all':
            challenges = [c for c in challenges if c['platform'] == platform or c['platform'] == 'all']
        
        # Apply limit
        challenges = challenges[:limit]
        
        # Convert to signals
        signals = []
        for challenge in challenges:
            signal = self._create_signal(challenge)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a signal from challenge data.
        
        Args:
            challenge: Raw challenge data
            
        Returns:
            Signal dictionary
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Calculate metrics
        participants = challenge.get('participants', 0)
        signal_strength = min(10.0, (participants / 1000000) * 2)  # Scale to 0-10
        
        signal = {
            'signal_type': 'challenge',
            'name': challenge.get('name', 'Unknown Challenge'),
            'source': self.get_source_name(),
            'signal_id': f"{challenge.get('hashtag', 'unknown')}_{int(time.time())}",
            'first_seen': timestamp,
            'last_seen': timestamp,
            'description': challenge.get('description', ''),
            'tags': [
                'challenge',
                challenge.get('platform', 'social'),
                challenge.get('category', 'general')
            ],
            'metrics': {
                'signal_strength': signal_strength,
                'volume': participants,
                'virality': min(1.0, participants / 10000000)  # 0-1 scale
            },
            'temporal': {
                'first_observed': timestamp,
                'last_updated': timestamp,
                'current_status': 'active'
            },
            'extra': {
                'platform': challenge.get('platform', 'unknown'),
                'hashtag': challenge.get('hashtag', ''),
                'category': challenge.get('category', 'general'),
                'origin_date': challenge.get('origin_date', ''),
                'participants': participants
            }
        }
        
        return signal
