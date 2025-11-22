# Virtual Environment Strategy

**Decision Date**: 2025-10-31  
**Status**: ✅ IMPLEMENTED  
**Related Issues**: #113, #115, #118

## Executive Summary

**IMPLEMENTED STRATEGY: Per-Project Virtual Environments (Full Isolation)**

This decision is driven by the technical requirement that each project in the PrismQ.T.Idea.Inspiration ecosystem uses AI libraries with potentially different versions. Python cannot install multiple versions of the same package (e.g., PyTorch 2.0.0 and PyTorch 2.1.0) in a single environment, making full isolation the only viable approach.

## The Decision

### ✅ Implemented
- **Issue #115**: Per-Project Virtual Environments
- **Issue #118**: direnv Auto-Activation

### ❌ Not Implemented
- **Issue #114**: Shared Virtual Environment (technically impossible with AI)
- **Issue #116**: Grouped Virtual Environments (conflicts with AI in grouped projects)
- **Issue #117**: Layered Hybrid Virtual Environments (over-complex, doesn't solve AI conflicts)

## Why Per-Project Isolation?

### Technical Requirements

**Critical Constraint**: Each project depends on AI tools with potentially different versions.

**The Problem**:
- You **cannot** install PyTorch 2.0.0 AND PyTorch 2.1.0 in the same environment
- You **cannot** install transformers 4.30 AND transformers 4.35 in the same environment
- Different AI projects need different frameworks, models, and versions

**The Solution**:
- Only per-project isolation allows each project to use its required AI stack
- Sharing or grouping AI dependencies is **technically impossible**

### Real-World Example

```
Classification Project:
  - Uses BERT models
  - Needs: torch==2.0.0, transformers==4.30.0

Sources Project:
  - Uses GPT/Llama models  
  - Needs: torch==2.1.0, transformers==4.35.0

Problem in Shared Environment:
  - Cannot install both torch 2.0.0 and 2.1.0
  - Cannot install both transformers 4.30 and 4.35
  - Result: DEADLOCK, projects cannot both work
```

## Project Structure

```
PrismQ.T.Idea.Inspiration/
├── Classification/
│   └── venv/          # ~4-5GB (PyTorch + BERT models)
├── Model/
│   └── venv/          # ~180MB (no AI, pure Python)
├── EnvLoad/
│   └── venv/          # ~200MB (no AI, config only)
├── Sources/
│   └── venv/          # ~4-5GB (PyTorch + GPT models)
├── Scoring/
│   └── venv/          # ~5-6GB (PyTorch + multi-modal models)
└── Client/Backend/
    └── venv/          # ~4-5GB (AI for user interactions)

Total: ~20-30GB
```

## Setup Instructions

### Automated Setup (Recommended)

```bash
# Linux/macOS/WSL
cd PrismQ.T.Idea.Inspiration
./_meta/_scripts/setup_all_envs.sh

# Windows PowerShell
cd PrismQ.T.Idea.Inspiration
.\_meta\_scripts\setup_all_envs.ps1

# Windows CMD
cd PrismQ.T.Idea.Inspiration
.\_meta\_scripts\setup_all_envs.bat
```

These scripts will:
1. Create a virtual environment in each project directory
2. Install project-specific dependencies from `requirements.txt`
3. Verify installation and run tests

### Manual Setup (Per Project)

```bash
# Navigate to a project
cd Classification

# Create virtual environment
python -m venv venv

# Activate environment
# Linux/macOS/WSL:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest
```

## direnv Auto-Activation (Optional but Recommended)

direnv automatically activates the correct virtual environment when you `cd` into a project directory, eliminating manual activation steps.

### Installation

**Ubuntu/Debian**:
```bash
sudo apt install direnv
```

**macOS**:
```bash
brew install direnv
```

**Windows**: See [DIRENV_SETUP.md](../DIRENV_SETUP.md) for detailed Windows setup

### Configuration

1. Add direnv hook to your shell configuration:

**Bash** (`~/.bashrc`):
```bash
eval "$(direnv hook bash)"
```

**Zsh** (`~/.zshrc`):
```bash
eval "$(direnv hook zsh)"
```

**PowerShell** (`$PROFILE`):
```powershell
Invoke-Expression "$(direnv hook pwsh)"
```

2. Allow direnv for each project (one-time per project):
```bash
cd Classification
direnv allow

cd ../Sources
direnv allow
# ... repeat for all projects
```

### Developer Workflow with direnv

```bash
# Navigate to project - environment auto-activates
cd Classification/
# → Classification venv automatically activated
# → Correct PyTorch, transformers, CUDA settings loaded

cd ../Sources/
# → Sources venv automatically activated  
# → Different PyTorch, different transformers loaded
# → Zero manual intervention
```

## Benefits

1. **Zero AI Conflicts**: Each project has its own AI stack, no version conflicts
2. **Independent Choices**: Classification uses BERT, Sources uses GPT, Scoring uses CLIP
3. **Safe Experimentation**: Test new AI models in one project without breaking others
4. **Team Independence**: ML team, web team, data team work without coordination
5. **Production Parity**: Development matches deployed containers (each service isolated)
6. **Seamless Switching**: With direnv, environments activate automatically

## Maintenance

### Updating Dependencies

**Single Project**:
```bash
cd Classification
source venv/bin/activate  # or let direnv handle it
pip install --upgrade package-name
pip freeze > requirements.txt
```

**All Projects**:
```bash
# Linux/macOS/WSL
./_meta/_scripts/update_all_envs.sh

# Windows PowerShell
.\_meta\_scripts\update_all_envs.ps1
```

### Recreating Environments

If an environment becomes corrupted or needs to be recreated:

```bash
cd Classification
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Cost-Benefit Analysis

### Costs
- **Disk Space**: ~30GB total (acceptable on modern development machines)
- **Setup Time**: ~30-60 minutes one-time (automated)
- **Maintenance**: Minimal (scripts handle updates automatically)

### Benefits
- **AI Freedom**: Each project chooses its AI stack freely (priceless)
- **Zero Conflicts**: Impossible to have AI version conflicts (priceless)
- **Development Speed**: No coordination overhead between teams (high value)
- **Debugging**: Know exactly which AI packages are active (high value)
- **Production Parity**: Dev environment matches deployment (best practice)

### ROI
**Infinite** - This is the only strategy that works with AI in each project.

## FAQs

### Q: Can't we just use the same PyTorch version across all projects?

**A**: No, because:
- Different AI models may require different PyTorch versions
- RTX 5090 needs specific CUDA versions that may vary by PyTorch version
- Different projects may use different AI frameworks entirely (some OpenAI API, some local models)
- Forcing all projects to use the same version limits AI choices

### Q: Won't 30GB of disk space be wasteful?

**A**: No, because:
- If projects need different AI package versions, you'd use ~30GB even with shared environment
- Modern development machines have 1-4TB drives; 30GB is <1%
- The cost of trying to save disk space (dependency conflicts) is much higher

### Q: What about maintenance overhead?

**A**: Minimal:
- `update_all_envs.sh` script updates all environments at once
- Each project maintains its own `requirements.txt` independently
- CI/CD is simpler (no version matrix testing needed)

## Related Documentation

- [DIRENV_SETUP.md](../DIRENV_SETUP.md) - Detailed direnv configuration guide
- [Complete Technical Analysis](../archive/decisions/VENV_STRATEGY_DECISION.md) - Full 800+ line analysis (archived)
- [Visual Decision Guide](../archive/decisions/VENV_STRATEGY_VISUAL_DECISION.md) - Visual comparison of strategies (archived)

## See Also

- Repository README: [/README.md](../../../README.md)
- Setup Scripts: `_meta/_scripts/setup_all_envs.*`
