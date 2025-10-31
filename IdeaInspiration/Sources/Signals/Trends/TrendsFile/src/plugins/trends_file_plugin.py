"""TrendsFile plugin for importing trend signals from CSV/JSON files."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
import json
import csv
import os
from pathlib import Path
from . import SignalPlugin


class TrendsFilePlugin(SignalPlugin):
    """Plugin for importing trend signals from CSV/JSON files."""
    
    def __init__(self, config):
        """Initialize TrendsFile plugin."""
        super().__init__(config)
        self.api = None
        print("TrendsFile initialized for file-based trend import")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "trends_file"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Import trend signals from files.
        
        Args:
            **kwargs: Additional parameters
                - file_path: Path to CSV/JSON file
                - format: File format ('csv' or 'json')
                - limit: Maximum number of trends to import
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        file_path = kwargs.get('file_path', None)
        file_format = kwargs.get('format', 'json')
        limit = kwargs.get('limit', None)
        
        try:
            if file_path and os.path.exists(file_path):
                print(f"Importing trends from file: {file_path}")
                if file_format == 'csv':
                    signals = self._import_from_csv(file_path, limit)
                elif file_format == 'json':
                    signals = self._import_from_json(file_path, limit)
                else:
                    raise ValueError(f"Unsupported format: {file_format}")
                print(f"Successfully imported {len(signals)} trend signals from file")
            else:
                print("Running in stub mode - returning sample trend data")
                signals = self._get_sample_trends(limit or 10)
                print(f"Successfully generated {len(signals)} sample trend signals")
            
        except Exception as e:
            print(f"Error importing trends from file: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _import_from_csv(self, file_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Import trends from CSV file.
        
        Args:
            file_path: Path to CSV file
            limit: Maximum number of trends to import
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if limit and i >= limit:
                    break
                
                # Parse tags if comma-separated
                tags = row.get('tags', '').split(',') if row.get('tags') else []
                tags = [t.strip() for t in tags if t.strip()]
                
                trend = {
                    'name': row.get('name', 'Unknown'),
                    'description': row.get('description', ''),
                    'volume': int(row.get('volume', 0)) if row.get('volume') else 0,
                    'tags': tags,
                    'first_seen': row.get('first_seen', '')
                }
                
                signal = self._create_signal(trend)
                signals.append(signal)
        
        return signals
    
    def _import_from_json(self, file_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Import trends from JSON file.
        
        Args:
            file_path: Path to JSON file
            limit: Maximum number of trends to import
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle both array and single object
            if not isinstance(data, list):
                data = [data]
            
            for i, item in enumerate(data):
                if limit and i >= limit:
                    break
                
                trend = {
                    'name': item.get('name', 'Unknown'),
                    'description': item.get('description', ''),
                    'volume': item.get('volume', 0),
                    'tags': item.get('tags', []),
                    'first_seen': item.get('first_seen', '')
                }
                
                signal = self._create_signal(trend)
                signals.append(signal)
        
        return signals
    
    def _get_sample_trends(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate sample trend data for testing.
        
        Args:
            limit: Number of trends to generate
            
        Returns:
            List of signal dictionaries
        """
        trends = [
            {
                'name': 'AI Video Generation',
                'description': 'Trending topic: AI-powered video creation tools',
                'volume': 5000000,
                'tags': ['ai', 'video', 'technology'],
                'first_seen': '2024-10-15T00:00:00Z'
            },
            {
                'name': 'Sustainable Fashion',
                'description': 'Growing interest in eco-friendly clothing',
                'volume': 3000000,
                'tags': ['fashion', 'sustainability', 'eco'],
                'first_seen': '2024-10-20T00:00:00Z'
            },
            {
                'name': 'Remote Work Tools',
                'description': 'Collaboration tools for distributed teams',
                'volume': 2500000,
                'tags': ['work', 'remote', 'productivity'],
                'first_seen': '2024-10-18T00:00:00Z'
            },
            {
                'name': 'Plant-Based Diet',
                'description': 'Vegan and vegetarian lifestyle trends',
                'volume': 4000000,
                'tags': ['food', 'health', 'vegan'],
                'first_seen': '2024-10-10T00:00:00Z'
            },
            {
                'name': 'Electric Vehicles',
                'description': 'EV adoption and charging infrastructure',
                'volume': 6000000,
                'tags': ['ev', 'automotive', 'sustainability'],
                'first_seen': '2024-10-05T00:00:00Z'
            },
            {
                'name': 'Mental Health Awareness',
                'description': 'Growing focus on mental wellness',
                'volume': 3500000,
                'tags': ['health', 'wellness', 'mental'],
                'first_seen': '2024-10-22T00:00:00Z'
            },
            {
                'name': 'Cryptocurrency Trading',
                'description': 'Digital asset investment trends',
                'volume': 5500000,
                'tags': ['crypto', 'finance', 'trading'],
                'first_seen': '2024-10-12T00:00:00Z'
            },
            {
                'name': 'Home Gardening',
                'description': 'Urban and indoor gardening popularity',
                'volume': 2000000,
                'tags': ['gardening', 'home', 'plants'],
                'first_seen': '2024-10-08T00:00:00Z'
            },
            {
                'name': 'Online Learning',
                'description': 'E-learning platform adoption growth',
                'volume': 4500000,
                'tags': ['education', 'online', 'learning'],
                'first_seen': '2024-10-16T00:00:00Z'
            },
            {
                'name': 'Smart Home Automation',
                'description': 'IoT and home automation trends',
                'volume': 3200000,
                'tags': ['smarthome', 'iot', 'technology'],
                'first_seen': '2024-10-14T00:00:00Z'
            }
        ]
        
        # Apply limit
        trends = trends[:limit]
        
        # Convert to signals
        signals = []
        for trend in trends:
            signal = self._create_signal(trend)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a signal from trend data.
        
        Args:
            trend: Raw trend data
            
        Returns:
            Signal dictionary
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Calculate metrics
        volume = trend.get('volume', 0)
        signal_strength = min(10.0, (volume / 1000000) * 2)  # Scale to 0-10
        
        # Use provided first_seen or current time
        first_seen = trend.get('first_seen', timestamp)
        
        signal = {
            'signal_type': 'trend',
            'name': trend.get('name', 'Unknown Trend'),
            'source': self.get_source_name(),
            'signal_id': f"{trend.get('name', 'unknown').replace(' ', '_')}_{int(time.time())}",
            'first_seen': first_seen,
            'last_seen': timestamp,
            'description': trend.get('description', ''),
            'tags': ['trend', 'imported'] + (trend.get('tags', []) if isinstance(trend.get('tags'), list) else []),
            'metrics': {
                'signal_strength': signal_strength,
                'volume': volume,
                'virality': min(1.0, volume / 10000000)  # 0-1 scale
            },
            'temporal': {
                'first_observed': first_seen,
                'last_updated': timestamp,
                'current_status': 'active'
            },
            'extra': {
                'source_type': 'file_import',
                'volume': volume
            }
        }
        
        return signal
