"""CSV parsing and data transformation for CSV Import source."""

import pandas as pd
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class CSVParser:
    """Parses CSV files and transforms data to IdeaInspiration format.
    
    Follows Single Responsibility Principle (SRP) by focusing only on
    CSV parsing and data transformation.
    """
    
    # Expected column mappings (flexible)
    COLUMN_MAPPING = {
        'title': ['title', 'idea', 'name', 'heading'],
        'description': ['description', 'desc', 'details', 'content', 'body'],
        'category': ['category', 'cat', 'type', 'topic'],
        'priority': ['priority', 'pri', 'importance'],
        'tags': ['tags', 'labels', 'keywords'],
        'status': ['status', 'state', 'stage'],
        'notes': ['notes', 'note', 'comments', 'remarks'],
        'created_by': ['created_by', 'creator', 'author', 'owner'],
        'assigned_to': ['assigned_to', 'assignee', 'assigned'],
    }
    
    def __init__(self, default_priority: str = 'medium',
                 default_status: str = 'new',
                 default_category: str = 'general',
                 delimiter: str = ',',
                 encoding: str = 'utf-8'):
        """Initialize CSV parser.
        
        Args:
            default_priority: Default priority for ideas (default: 'medium')
            default_status: Default status for ideas (default: 'new')
            default_category: Default category for ideas (default: 'general')
            delimiter: CSV delimiter (default: ',')
            encoding: File encoding (default: 'utf-8')
        """
        self.default_priority = default_priority
        self.default_status = default_status
        self.default_category = default_category
        self.delimiter = delimiter
        self.encoding = encoding
    
    def parse_file(self, file_path: str, batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse CSV file and convert to IdeaInspiration format.
        
        Args:
            file_path: Path to CSV file
            batch_id: Optional batch identifier for tracking
            
        Returns:
            List of idea dictionaries in IdeaInspiration format
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Generate batch ID if not provided
        if batch_id is None:
            batch_id = self._generate_batch_id(file_path)
        
        try:
            # Try reading as CSV
            df = pd.read_csv(file_path, delimiter=self.delimiter, encoding=self.encoding)
        except Exception as e:
            # Try reading as Excel if CSV fails
            try:
                df = pd.read_excel(file_path)
            except Exception as excel_error:
                raise ValueError(f"Failed to parse file as CSV or Excel: {e}, {excel_error}")
        
        # Normalize column names (lowercase, strip whitespace)
        df.columns = df.columns.str.lower().str.strip()
        
        # Transform rows to IdeaInspiration format
        ideas = []
        for idx, row in df.iterrows():
            idea = self._transform_row(row, idx, batch_id, file_path)
            if idea:
                ideas.append(idea)
        
        return ideas
    
    def _transform_row(self, row: pd.Series, row_idx: int, 
                      batch_id: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Transform a CSV row to IdeaInspiration format.
        
        Args:
            row: Pandas Series representing a row
            row_idx: Row index
            batch_id: Batch identifier
            file_path: Source file path
            
        Returns:
            Idea dictionary or None if row is invalid
        """
        # Extract title (required)
        title = self._get_column_value(row, 'title')
        if not title or pd.isna(title):
            # Skip rows without title
            return None
        
        # Extract other fields with defaults
        description = self._get_column_value(row, 'description', '')
        category = self._get_column_value(row, 'category', self.default_category)
        priority = self._get_column_value(row, 'priority', self.default_priority)
        status = self._get_column_value(row, 'status', self.default_status)
        notes = self._get_column_value(row, 'notes', '')
        created_by = self._get_column_value(row, 'created_by', '')
        assigned_to = self._get_column_value(row, 'assigned_to', '')
        
        # Parse tags (comma-separated or list)
        tags_raw = self._get_column_value(row, 'tags', '')
        if isinstance(tags_raw, str):
            tags = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]
        elif isinstance(tags_raw, list):
            tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]
        else:
            tags = []
        
        # Generate unique source_id
        source_id = self._generate_source_id(title, description, row_idx, file_path)
        
        # Current timestamp
        now = datetime.now().isoformat()
        
        # Calculate age_days (0 for new imports)
        age_days = 0
        
        # Calculate basic priority score
        priority_score = self._calculate_priority_score(priority)
        
        # Calculate actionability (default medium value)
        actionability = 5.0
        
        # Build IdeaInspiration format
        idea = {
            'source': 'csv_import',
            'source_id': source_id,
            'idea': {
                'title': str(title).strip(),
                'description': str(description).strip() if description else '',
                'notes': str(notes).strip() if notes else '',
                'category': str(category).strip(),
                'priority': str(priority).strip().lower()
            },
            'metadata': {
                'status': str(status).strip().lower(),
                'created_by': str(created_by).strip() if created_by else '',
                'assigned_to': str(assigned_to).strip() if assigned_to else '',
                'tags': tags
            },
            'tracking': {
                'created_at': now,
                'modified_at': now,
                'used_at': None,
                'age_days': age_days
            },
            'universal_metrics': {
                'priority_score': priority_score,
                'actionability': actionability
            },
            'import_batch': batch_id,
            'import_timestamp': now
        }
        
        return idea
    
    def _get_column_value(self, row: pd.Series, field: str, default: Any = None) -> Any:
        """Get value from row using flexible column mapping.
        
        Args:
            row: Pandas Series
            field: Field name to look for
            default: Default value if not found
            
        Returns:
            Column value or default
        """
        # Get possible column names for this field
        possible_names = self.COLUMN_MAPPING.get(field, [field])
        
        # Try each possible name
        for col_name in possible_names:
            if col_name in row.index:
                value = row[col_name]
                # Return value if not NaN
                if pd.notna(value):
                    return value
        
        return default
    
    def _generate_source_id(self, title: str, description: str, 
                           row_idx: int, file_path: str) -> str:
        """Generate unique source ID for an idea.
        
        Args:
            title: Idea title
            description: Idea description
            row_idx: Row index
            file_path: Source file path
            
        Returns:
            Unique source ID
        """
        # Combine fields for uniqueness
        unique_string = f"{file_path}|{row_idx}|{title}|{description}"
        
        # Generate hash
        hash_obj = hashlib.sha256(unique_string.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars
        
        return f"csv_{hash_hex}"
    
    def _generate_batch_id(self, file_path: str) -> str:
        """Generate batch ID based on file path and timestamp.
        
        Args:
            file_path: Source file path
            
        Returns:
            Batch ID string
        """
        file_name = Path(file_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{file_name}_{timestamp}"
    
    def _calculate_priority_score(self, priority: str) -> float:
        """Calculate numeric priority score from priority string.
        
        Args:
            priority: Priority string (high, medium, low)
            
        Returns:
            Priority score (0-10)
        """
        priority_lower = str(priority).lower().strip()
        
        priority_map = {
            'high': 8.0,
            'medium': 5.0,
            'low': 2.0,
            'critical': 10.0,
            'urgent': 9.0,
            'normal': 5.0,
            'minor': 3.0
        }
        
        return priority_map.get(priority_lower, 5.0)
    
    def validate_csv_structure(self, file_path: str) -> Dict[str, Any]:
        """Validate CSV structure and return diagnostic information.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with validation results
        """
        try:
            df = pd.read_csv(file_path, delimiter=self.delimiter, encoding=self.encoding)
        except Exception as e:
            try:
                df = pd.read_excel(file_path)
            except:
                return {
                    'valid': False,
                    'error': f"Cannot parse file: {e}",
                    'suggestions': ['Check file format (CSV or Excel)', 'Verify encoding']
                }
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        columns = df.columns.tolist()
        
        # Check for required columns
        has_title = any(col in columns for col in self.COLUMN_MAPPING['title'])
        
        # Gather diagnostic info
        validation = {
            'valid': has_title,
            'total_rows': len(df),
            'columns': columns,
            'has_title': has_title,
            'has_description': any(col in columns for col in self.COLUMN_MAPPING['description']),
            'has_category': any(col in columns for col in self.COLUMN_MAPPING['category']),
            'has_priority': any(col in columns for col in self.COLUMN_MAPPING['priority']),
            'has_tags': any(col in columns for col in self.COLUMN_MAPPING['tags']),
            'has_status': any(col in columns for col in self.COLUMN_MAPPING['status']),
        }
        
        if not has_title:
            validation['error'] = "Missing required 'title' column"
            validation['suggestions'] = [
                f"Add one of these column names: {', '.join(self.COLUMN_MAPPING['title'])}",
                "Current columns: " + ", ".join(columns)
            ]
        
        return validation
