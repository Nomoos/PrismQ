# Script Standardization Recommendation

**Date:** 2025-10-31  
**Status:** Recommended  
**Scope:** All PrismQ.IdeaInspiration modules

## Executive Summary

For the PrismQ.IdeaInspiration repository, **PowerShell (.ps1)** is recommended as the primary scripting format for Windows automation scripts, with batch scripts (.bat) maintained for legacy support.

## Problem Statement

The repository currently has a mix of scripting formats:
- Batch scripts (.bat) - Simple but limited
- Shell scripts (.sh) - For Linux/CI
- PowerShell scripts (.ps1) - Used in Client module only

This inconsistency creates confusion about which script format to use, especially when working with AI assistants like GitHub Copilot and ChatGPT.

## Recommendation

### Primary: PowerShell (.ps1) for Windows

**Use PowerShell as the recommended scripting format for all Windows automation.**

#### Rationale

1. **AI Assistant Friendly**
   - Structured, readable syntax that AI tools understand better
   - Clear intent with explicit cmdlets vs cryptic batch commands
   - Better for code generation and modification by GitHub Copilot/ChatGPT
   - More natural language-like commands

2. **Better Error Handling**
   - Try/catch/finally blocks for structured error handling
   - `$LASTEXITCODE` for checking command results
   - `-ErrorAction` parameter for fine-grained control
   - Better error messages with color-coded output

3. **Modern Windows Standard**
   - Built into Windows 10/11 (PowerShell 5.1+)
   - Microsoft's recommended scripting platform
   - Cross-platform with PowerShell 7+ (Core)
   - Active development and community support

4. **Enhanced Capabilities**
   - Object-oriented pipeline (not just text)
   - Native .NET integration
   - Rich set of built-in cmdlets
   - Better string manipulation and data handling
   - Support for functions, modules, and advanced features

5. **Developer Experience**
   - Colored console output for better readability
   - Tab completion and IntelliSense in editors
   - Consistent parameter naming conventions
   - Better debugging capabilities

6. **Platform Alignment**
   - Windows is the primary target platform (RTX 5090, AMD Ryzen)
   - PowerShell is the native Windows scripting solution
   - Better integration with Windows features

### Secondary: Batch (.bat) for Legacy Support

**Maintain batch scripts for users who cannot or prefer not to use PowerShell.**

#### When to Use Batch

- Execution policy restrictions prevent PowerShell
- Maximum compatibility requirements
- Simple, one-liner commands
- CI/CD environments that don't support PowerShell

### Tertiary: Shell (.sh) for Linux/CI

**Maintain shell scripts for Linux testing and CI/CD pipelines.**

#### When to Use Shell Scripts

- Linux development/testing environments
- GitHub Actions or other CI/CD
- Docker containers
- Cross-platform testing (though Windows is primary)

## Implementation Strategy

### For New Scripts

1. **Create PowerShell version first** (.ps1)
2. **Optionally create batch version** (.bat) for compatibility
3. **Create shell version if needed** (.sh) for Linux/CI

### For Existing Scripts

1. **Add PowerShell versions** alongside existing batch scripts
2. **Update documentation** to recommend PowerShell
3. **Keep batch scripts** for backward compatibility
4. **Don't remove** existing working scripts

### Script Naming Convention

- `setup.ps1` / `setup.bat` / `setup.sh`
- `run.ps1` / `run.bat` / `run.sh`
- `test.ps1` / `test.bat` / `test.sh`
- etc.

## PowerShell Best Practices

### 1. Execution Policy

Scripts should include guidance on enabling PowerShell:

```powershell
# Run once to enable local scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Error Handling

```powershell
try {
    python --version
    Write-Host "✅ Python found!" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found" -ForegroundColor Red
    exit 1
}
```

### 3. Exit Codes

```powershell
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Command failed" -ForegroundColor Red
    exit 1
}
```

### 4. User Feedback

```powershell
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
```

### 5. Path Handling

```powershell
# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..\..")
```

## Documentation Standards

### README.md Structure

1. List PowerShell scripts first (recommended)
2. Mention batch scripts as legacy/compatibility option
3. Include "Why PowerShell?" section
4. Provide execution policy instructions
5. Show usage examples for all script types

### Example Documentation

```markdown
### Setup Scripts

**Windows (PowerShell): `setup.ps1` (Recommended)**
- Enhanced error handling and colored output
- Better for AI assistants (GitHub Copilot/ChatGPT)

**Windows (Batch): `setup.bat`**
- Legacy batch script for compatibility
- Use if you cannot run PowerShell scripts

**Linux: `setup.sh`**
- For testing purposes only
```

## Migration Plan

### Phase 1: YouTube Module (Completed)
- ✅ Create `setup.ps1` and `run.ps1`
- ✅ Update README.md
- ✅ Document PowerShell benefits

### Phase 2: Other Modules (Recommended)

Apply the same pattern to:
- Classification module
- Scoring module
- EnvLoad module
- Model module
- Client module (already has .ps1)

For each module:
1. Create PowerShell versions of existing batch scripts
2. Update module README.md
3. Test scripts on Windows
4. Maintain batch scripts for compatibility

### Phase 3: Repository-Wide (Future)

- Add PowerShell examples to CONTRIBUTING.md
- Create script templates in RepositoryTemplate
- Update CI/CD to prefer PowerShell on Windows runners

## Comparison Matrix

| Feature | PowerShell | Batch | Shell |
|---------|-----------|-------|-------|
| Windows Native | ✅ Excellent | ✅ Good | ❌ Requires WSL/Git Bash |
| Error Handling | ✅ Excellent | ⚠️ Limited | ✅ Good |
| Readability | ✅ Excellent | ⚠️ Poor | ✅ Good |
| AI-Friendly | ✅ Excellent | ❌ Poor | ✅ Good |
| Colored Output | ✅ Built-in | ⚠️ Via echo | ✅ Built-in |
| Learning Curve | ⚠️ Moderate | ✅ Easy | ⚠️ Moderate |
| Debugging | ✅ Excellent | ❌ Poor | ✅ Good |
| Modern Features | ✅ Excellent | ❌ Limited | ✅ Good |
| Cross-Platform | ✅ PS Core | ❌ Windows only | ✅ Excellent |
| Legacy Support | ✅ Good | ✅ Excellent | ❌ Limited |

## Common Objections

### "PowerShell scripts are blocked by execution policy"

**Response:** This is a one-time setup. Users run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This is documented in the README with clear instructions.

### "Batch scripts are simpler"

**Response:** For simple tasks, yes. But our scripts need:
- Error handling
- Colored output
- Virtual environment management
- User interaction
- These features are easier and cleaner in PowerShell

### "Not everyone knows PowerShell"

**Response:** 
- PowerShell syntax is more intuitive than batch
- Better documentation available
- AI assistants can help (which is part of the goal)
- We maintain batch scripts for those who prefer them

### "What about Mac/Linux developers?"

**Response:**
- Windows is the primary platform (per requirements)
- We maintain `.sh` scripts for Linux testing
- PowerShell Core works on Mac/Linux if needed
- CI/CD can use shell scripts

## Conclusion

PowerShell is the recommended scripting format for PrismQ.IdeaInspiration because:

1. ✅ **Better for AI assistants** (GitHub Copilot, ChatGPT)
2. ✅ **Modern Windows standard**
3. ✅ **Superior error handling**
4. ✅ **Enhanced user experience** (colors, formatting)
5. ✅ **More maintainable** code
6. ✅ **Aligns with target platform** (Windows primary)

While batch scripts remain for compatibility, PowerShell should be the recommended and documented primary option going forward.

## References

- [Microsoft PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [PowerShell Best Practices](https://docs.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-development-guidelines)
- [PowerShell vs Batch](https://stackoverflow.com/questions/6726267/batch-vs-powershell)
- [GitHub Copilot Instructions](.github/copilot-instructions.md)

## Appendix: Example Scripts

See implementation in:
- `Sources/Content/Shorts/YouTube/_meta/_scripts/setup.ps1`
- `Sources/Content/Shorts/YouTube/_meta/_scripts/run.ps1`
- `Sources/Content/Shorts/YouTube/_meta/_scripts/README.md`
