"""CSV Import plugin for importing ideas from CSV/Excel files."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from . import SourcePlugin, IdeaInspiration
from ..core.csv_parser import CSVParser


class CSVImportPlugin(SourcePlugin):
    """Plugin for importing ideas from CSV and Excel files."""
    
    def __init__(self, config):
        """Initialize CSV import plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Initialize CSV parser with config defaults
        self.parser = CSVParser(
            default_priority=config.default_priority,
            default_status=config.default_status,
            default_category=config.default_category,
            delimiter=config.csv_delimiter,
            encoding=config.csv_encoding
        )
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "csv_import"
    
    def scrape(self, file_path: Optional[str] = None, 
              batch_id: Optional[str] = None) -> List[IdeaInspiration]:
        """Import ideas from CSV/Excel file.
        
        Args:
            file_path: Path to CSV/Excel file (optional, uses config if not provided)
            batch_id: Optional batch identifier for tracking
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        # Use config value if not provided
        if file_path is None:
            file_path = getattr(self.config, 'default_csv_path', None)
            if not file_path:
                print("Error: No CSV file path provided and none configured")
                return ideas
        
        # Verify file exists
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return ideas
        
        print(f"Importing ideas from: {file_path}")
        
        # Validate CSV structure
        validation = self.parser.validate_csv_structure(file_path)
        
        if not validation['valid']:
            print(f"Error: Invalid CSV structure")
            print(f"  {validation.get('error', 'Unknown error')}")
            if 'suggestions' in validation:
                for suggestion in validation['suggestions']:
                    print(f"  - {suggestion}")
            return ideas
        
        print(f"CSV validation passed:")
        print(f"  - Total rows: {validation['total_rows']}")
        print(f"  - Has title: {validation['has_title']}")
        print(f"  - Has description: {validation['has_description']}")
        print(f"  - Has category: {validation['has_category']}")
        print(f"  - Columns: {', '.join(validation['columns'])}")
        
        # Parse CSV file
        try:
            ideas_data = self.parser.parse_file(file_path, batch_id)
            print(f"\nSuccessfully parsed {len(ideas_data)} ideas from CSV")
            
            # Transform to IdeaInspiration objects
            for idea_data in ideas_data:
                idea = self._transform_csv_row_to_idea(idea_data, file_path, batch_id)
                ideas.append(idea)
                
        except Exception as e:
            print(f"Error parsing CSV file: {e}")
            return []
        
        return ideas
    
    def import_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Import ideas from multiple CSV/Excel files.
        
        Args:
            file_paths: List of paths to CSV/Excel files
            
        Returns:
            Dictionary with import results
        """
        results = {
            'total_files': len(file_paths),
            'successful_files': 0,
            'failed_files': 0,
            'total_ideas': 0,
            'file_results': []
        }
        
        for file_path in file_paths:
            print(f"\n{'='*60}")
            print(f"Processing file: {file_path}")
            print(f"{'='*60}")
            
            try:
                ideas = self.scrape(file_path)
                
                file_result = {
                    'file_path': file_path,
                    'success': True,
                    'ideas_count': len(ideas),
                    'error': None
                }
                
                results['successful_files'] += 1
                results['total_ideas'] += len(ideas)
                
            except Exception as e:
                file_result = {
                    'file_path': file_path,
                    'success': False,
                    'ideas_count': 0,
                    'error': str(e)
                }
                results['failed_files'] += 1
            
            results['file_results'].append(file_result)
        
        return results
    
    def _transform_csv_row_to_idea(self, idea_data: Dict[str, Any], file_path: str, batch_id: Optional[str] = None) -> IdeaInspiration:
        """Transform CSV row data to IdeaInspiration object.
        
        Args:
            idea_data: Idea data dictionary from CSV parser
            file_path: Path to source CSV file
            batch_id: Optional batch identifier
            
        Returns:
            IdeaInspiration object
        """
        title = idea_data.get('title', 'Untitled')
        description = idea_data.get('description', '')
        tags = idea_data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        tags = self.format_tags(tags + ['csv_import', 'imported'])
        
        # Build metadata with string values
        metadata = {
            'source_file': str(Path(file_path).name),
            'batch_id': batch_id if batch_id else '',
            'category': idea_data.get('category', ''),
            'priority': str(idea_data.get('priority', '')),
            'status': idea_data.get('status', ''),
            'notes': idea_data.get('notes', ''),
            'import_date': datetime.now(timezone.utc).isoformat() + 'Z',
        }
        
        # Add any custom columns to metadata
        for key, value in idea_data.items():
            if key not in ['title', 'description', 'tags', 'category', 'priority', 'status', 'notes']:
                metadata[f'custom_{key}'] = str(value)
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=title,
            description=description,
            text_content=idea_data.get('content', description),
            keywords=tags,
            metadata=metadata,
            source_id=f"csv_{Path(file_path).stem}_{hash(title)}",
            source_url='',  # No URL for CSV imports
            source_platform="csv_import",
            source_created_by="CSV Import",
            source_created_at=datetime.now(timezone.utc).isoformat() + 'Z',
            category=idea_data.get('category')
        )
        
        return idea
