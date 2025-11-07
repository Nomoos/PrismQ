# Model Module - Setup Guide

## Database Setup

### Windows (Primary Platform)

Run the setup script to create the database in your working directory:

**PowerShell (Recommended):**
```powershell
.\setup_db.ps1
```

**Batch (Legacy):**
```batch
setup_db.bat
```

This script will:
- Set up `.env` configuration in your working directory (creates one if missing)
- Remember your working directory for future use
- Store configuration values (Python executable, working directory) in `.env`
- Create `db.s3db` in your configured working directory
- Create the `IdeaInspiration` table with the complete data model
- Never ask for current directory - uses remembered working directory from `.env`

**Why PowerShell?** PowerShell scripts provide better error handling, colored output, and are more AI-friendly (GitHub Copilot/ChatGPT). If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/macOS (CI/Testing)

For CI environments and testing on Linux/macOS:

```bash
./setup_db.sh
```

This script provides the same functionality optimized for non-interactive CI environments.

## Installation

### From Source

```bash
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.Model.git
cd PrismQ.IdeaInspiration.Model
pip install -e .
```

### For Development

```bash
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.Model.git
cd PrismQ.IdeaInspiration.Model
pip install -e ".[dev]"
```

## Configuration Management

The package includes a configuration manager that:
- **Remembers your working directory** - Never asks for current directory again
- **Stores configuration in `.env`** - Creates and manages `.env` file in the nearest parent directory with "PrismQ" in its name
- **Shared configuration** - All PrismQ packages in the same directory tree share the same `.env` file
- **Automatic persistence** - Configuration values are saved and restored automatically
- **Interactive and non-interactive modes** - Works in both CI environments and manual usage

## Database Fields

The database will include the following fields:
- Basic fields: title, description, content, keywords
- Source fields: source_type, source_id, source_url, source_created_by, source_created_at, metadata
- Scoring fields: score, category, subcategory_relevance, contextual_category_scores
- Database system fields: id (auto-increment), created_at, updated_at (timestamps)

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Database Creation Issues

If database creation fails:
1. Check that Python is in your PATH
2. Verify you have write permissions to the working directory
3. Check that `.env` file is properly configured

### Configuration Issues

If configuration is not persisting:
1. Verify `.env` file exists
2. Check that the file is in a parent directory with "PrismQ" in its name
3. Ensure you have read/write permissions to the `.env` file

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
