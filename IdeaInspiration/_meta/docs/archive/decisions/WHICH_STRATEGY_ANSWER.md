# Which Strategy to Implement? - Direct Answer

**Date**: 2025-10-31  
**Question**: Which strategy (#114, #115, #116, or #117) should be implemented?

---

## Direct Answer

### ✅ IMPLEMENT THESE:

1. **Issue #115: Per-Project Virtual Environments**
2. **Issue #118: direnv Auto-Activation**

### ❌ DO NOT IMPLEMENT:

1. **Issue #114: Shared Virtual Environment** - Technically impossible with AI
2. **Issue #116: Grouped Virtual Environments** - Fails with AI in grouped projects  
3. **Issue #117: Layered Hybrid** - Over-complex, doesn't solve AI conflicts

---

## Why This Is The Only Choice

### Your New Requirement Changes Everything

> "Each project will somehow depend on AI, there will be a lot different (small count common modules) or other tools"

This single statement makes the decision trivial:

**You cannot install multiple versions of the same AI package in one Python environment.**

### The Technical Reality

```python
# What you need across projects:
Classification:  torch==2.0.0, transformers==4.30.0
Sources:         torch==2.1.0, transformers==4.35.0
Scoring:         torch==2.0.0, transformers==4.33.0

# What Python allows in ONE environment:
torch==???         # Can only pick ONE version
transformers==???  # Can only pick ONE version

# Result: IMPOSSIBLE to satisfy all projects in shared/grouped environment
```

### Your Stated Preferences Align Perfectly

1. **You said**: "I prefer full isolation"
   - **Strategy #115 provides**: Complete isolation per project ✅

2. **You said**: "Hard drive space... isn't problem at all"
   - **Strategy #115 needs**: ~30GB total
   - **Your constraint**: No problem ✅

3. **You said**: "Switching isn't problem at all"  
   - **Strategy #115 + #118**: Auto-switching with direnv (zero manual work) ✅

**Conclusion**: Your preferences and technical requirements both point to #115.

---

## What Each Strategy Would Look Like

### ❌ Strategy #114 (Shared): FAILS IMMEDIATELY

```
# Day 1: Setup shared environment
.venv/ (at repo root)

# Day 2: Classification adds AI
pip install torch==2.0.0 transformers==4.30.0
# ✅ Works

# Day 3: Sources adds AI  
pip install torch==2.1.0 transformers==4.35.0
# ❌ CONFLICT: torch 2.1 incompatible with 2.0
# ❌ CONFLICT: transformers 4.35 incompatible with 4.30
# 🔥 DEADLOCK: Cannot proceed
```

### ❌ Strategy #116 (Grouped): FAILS WHEN AI ADDED

```
# Setup: Group lightweight projects
.venv-core/  # Classification, Model, ConfigLoad, Sources

# Later: Classification needs BERT (torch 2.0, transformers 4.30)
# Later: Sources needs GPT (torch 2.1, transformers 4.35)
# 🔥 SAME PROBLEM: Cannot install both in .venv-core
```

### ✅ Strategy #115 (Per-Project): WORKS PERFECTLY

```
Classification/venv/  # torch==2.0.0, transformers==4.30.0 ✅
Sources/venv/         # torch==2.1.0, transformers==4.35.0 ✅
Scoring/venv/         # torch==2.0.0, transformers==4.33.0 ✅

# No conflicts - each project has exactly what it needs
# + direnv auto-switches when you cd between projects
```

---

## Decision Matrix

| Strategy | Can Handle AI in Each Project? | Aligns with "Full Isolation"? | Disk Space OK? | Switching OK? | **Viable?** |
|----------|--------------------------------|-------------------------------|----------------|---------------|-------------|
| #114 Shared | ❌ NO - Conflicts guaranteed | ❌ NO - Everything shared | ✅ YES | ✅ YES | ❌ **NO** |
| #115 Per-Project | ✅ YES - Each isolated | ✅ YES - Complete isolation | ✅ YES (~30GB) | ✅ YES (direnv) | ✅ **YES** |
| #116 Grouped | ❌ NO - Conflicts in groups | ⚠️ PARTIAL - Some sharing | ✅ YES | ✅ YES (direnv) | ❌ **NO** |
| #117 Layered | ❌ NO - Base layer conflicts | ⚠️ PARTIAL - Complex | ✅ YES | ✅ YES | ❌ **NO** |

**Only #115 passes all requirements.**

---

## Implementation Checklist

### Phase 1: Implement #115 (Per-Project Venvs)

- [ ] Create `_meta/_scripts/setup_all_envs.sh` (Linux/macOS)
- [ ] Create `_meta/_scripts/setup_all_envs.ps1` (Windows PowerShell)  
- [ ] Create `_meta/_scripts/setup_all_envs.bat` (Windows CMD)
- [ ] Update `.gitignore` to exclude `*/venv/`
- [ ] Run setup script to create all 6 venvs
- [ ] Test all project test suites
- [ ] Measure disk space usage

### Phase 2: Implement #118 (direnv)

- [ ] Install direnv on development machine
- [ ] Create `.envrc` for each project
- [ ] Configure direnv to auto-activate venv on `cd`
- [ ] Test auto-activation works
- [ ] Document Windows setup

### Phase 3: Documentation

- [ ] Create `VIRTUAL_ENV_SETUP.md` guide
- [ ] Update main README.md
- [ ] Create VS Code workspace template
- [ ] Create PyCharm configuration guide

### Phase 4: Close Unused Issues

- [ ] Close #114 (will not implement - conflicts with AI)
- [ ] Close #116 (will not implement - conflicts with AI)
- [ ] Close #117 (will not implement - over-complex)

---

## FAQs

### Q: Can't we just use the same PyTorch version across all projects?

**A**: No, because:
- Different AI models may require different PyTorch versions
- You're using RTX 5090, which needs specific CUDA versions
- Different projects may use different AI frameworks entirely (some OpenAI API, some local models)
- Forcing all projects to use the same version limits your AI choices

### Q: Won't 30GB of disk space be wasteful?

**A**: No, because:
- If projects need different AI package versions, you'd use ~30GB even with shared environment (can't avoid installing all versions)
- Modern development machines have 1-4TB drives, 30GB is <1%
- You explicitly said "disk space isn't a problem"
- The cost of trying to save disk space (dependency conflicts) is much higher

### Q: What if I don't like switching environments manually?

**A**: You won't have to:
- direnv (#118) auto-activates the correct environment when you `cd` into a project
- Zero manual `source venv/bin/activate` needed
- Seamless, transparent switching
- You explicitly said "switching isn't a problem"

### Q: What about maintenance overhead?

**A**: Minimal:
- `update_all_envs.sh` script updates all environments at once
- Each project maintains its own `requirements.txt` (they already do)
- CI/CD is simpler (no version matrix testing needed)

---

## The Bottom Line

**Implement**: #115 + #118

**Because**: 
1. It's the only strategy that works with AI in each project
2. It matches your preference for full isolation
3. It has no practical downsides given your constraints
4. It's a best practice that matches production deployment patterns

**Don't overthink it**: This isn't a trade-off decision. The AI requirement makes it the only viable path.

---

**Ready to start?** See Issue #115 for detailed implementation steps.
