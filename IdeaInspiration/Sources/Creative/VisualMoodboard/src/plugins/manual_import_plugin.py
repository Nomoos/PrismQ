"""Manual import plugin for curated visual resources."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import csv
from . import SourcePlugin


class ManualImportPlugin(SourcePlugin):
    """Plugin for manually importing curated visual resources."""

    def __init__(self, config):
        """Initialize manual import plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "manual"

    def scrape(self) -> List[Dict[str, Any]]:
        """This method is not used for manual import.
        
        Returns:
            Empty list
        """
        return []

    def import_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Import visual resources from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of visual resource dictionaries
            
        Expected JSON format:
        [
            {
                "title": "Song Title - Artist",
                "content": "Lyric snippet text...",
                "creator": "Artist Name",
                "work_title": "Song Title",
                "themes": ["love", "loss"],
                "mood": "melancholic",
                "style": "modern",
                "license": "All Rights Reserved",
                "emotional_impact": 8.5,
                "versatility": 6.0,
                "inspiration_value": 7.5
            }
        ]
        """
        resources = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
            
            for i, item in enumerate(data):
                # Generate source_id from index
                source_id = f"manual_{Path(file_path).stem}_{i}"
                
                # Extract or use defaults
                title = item.get('title', f'Untitled {i}')
                content = item.get('content', '')
                
                # Build tags from themes
                themes = item.get('themes', [])
                tags = ','.join(['manual', 'lyrics'] + themes)
                
                resource = {
                    'source_id': source_id,
                    'title': title,
                    'content': content,
                    'tags': tags,
                    'metrics': item  # Pass full item for CreativeMetrics
                }
                resources.append(resource)
                
        except Exception as e:
            print(f"Error importing from JSON {file_path}: {e}")
        
        return resources

    def import_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Import visual resources from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of visual resource dictionaries
            
        Expected CSV format:
        title,content,creator,work_title,themes,mood,style,license,emotional_impact,versatility,inspiration_value
        "Song - Artist","Lyrics...","Artist","Song","love,loss","melancholic","modern","All Rights Reserved",8.5,6.0,7.5
        """
        resources = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    # Generate source_id
                    source_id = f"manual_{Path(file_path).stem}_{i}"
                    
                    # Extract fields
                    title = row.get('title', f'Untitled {i}')
                    content = row.get('content', '')
                    
                    # Parse themes
                    themes_str = row.get('themes', '')
                    themes = [t.strip() for t in themes_str.split(',') if t.strip()]
                    
                    # Build tags
                    tags = ','.join(['manual', 'lyrics'] + themes)
                    
                    # Build metrics dict
                    metrics = {
                        'title': title,
                        'creator': row.get('creator'),
                        'work_title': row.get('work_title'),
                        'themes': themes,
                        'mood': row.get('mood'),
                        'style': row.get('style'),
                        'license': row.get('license'),
                        'type': 'lyrics',
                        'format': 'text'
                    }
                    
                    # Parse numeric scores
                    for metric in ['emotional_impact', 'versatility', 'inspiration_value']:
                        value = row.get(metric)
                        if value:
                            try:
                                metrics[metric] = float(value)
                            except ValueError:
                                pass
                    
                    resource = {
                        'source_id': source_id,
                        'title': title,
                        'content': content,
                        'tags': tags,
                        'metrics': metrics
                    }
                    resources.append(resource)
                    
        except Exception as e:
            print(f"Error importing from CSV {file_path}: {e}")
        
        return resources

    def import_single(self, title: str, content: str, creator: Optional[str] = None,
                     work_title: Optional[str] = None, themes: Optional[List[str]] = None,
                     mood: Optional[str] = None, style: Optional[str] = None,
                     license_type: Optional[str] = None, emotional_impact: float = 5.0,
                     versatility: float = 5.0, inspiration_value: float = 5.0) -> Dict[str, Any]:
        """Import a single visual resource.
        
        Args:
            title: Display title
            content: Lyric snippet text
            creator: Artist/creator name
            work_title: Original work title
            themes: List of themes
            mood: Mood descriptor
            style: Style descriptor
            license_type: License type
            emotional_impact: 0-10 score
            versatility: 0-10 score
            inspiration_value: 0-10 score
            
        Returns:
            Lyric snippet dictionary
        """
        import hashlib
        
        # Generate source_id from content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        source_id = f"manual_{content_hash}"
        
        themes = themes or []
        tags = ','.join(['manual', 'lyrics'] + themes)
        
        metrics = {
            'title': title,
            'creator': creator,
            'work_title': work_title,
            'themes': themes,
            'mood': mood,
            'style': style,
            'license': license_type,
            'type': 'lyrics',
            'format': 'text',
            'emotional_impact': emotional_impact,
            'versatility': versatility,
            'inspiration_value': inspiration_value
        }
        
        resource = {
            'source_id': source_id,
            'title': title,
            'content': content,
            'tags': tags,
            'metrics': metrics
        }
        
        return resource
