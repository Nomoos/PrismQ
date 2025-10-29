param(
    [string]$BaseRepoPrefix = "https://github.com/Nomoos/PrismQ.IdeaInspiration",
    [switch]$DryRun
)

Write-Host "Base repo prefix: $BaseRepoPrefix"
Write-Host "Scanning immediate subfolders starting with an uppercase letter..."

$folders = Get-ChildItem -Directory | Where-Object { $_.Name -cmatch '^[A-Z]' } | Select-Object -ExpandProperty Name

if (-not $folders) {
    Write-Host "No matching folders found."
    exit 0
}

foreach ($name in $folders) {
    $remote = "$BaseRepoPrefix.$name.git"
    Write-Host "`n=== $name ==="
    Write-Host "Remote: $remote"

    if ($DryRun) {
        Write-Host "[DRY RUN] Would process folder $name"
        continue
    }

    Push-Location $name

    if (-not (Test-Path ".git")) {
        git init
    }

    # Ensure we have a clean 'origin' pointing to the right URL
    git remote remove origin 2>$null
    git remote add origin $remote

    # Try to fetch; if remote exists and is non-empty, checkout main from origin
    git fetch origin 2>$null

    # Check if origin/main exists
    $hasOriginMain = git ls-remote --heads origin main 2>$null
    if ($hasOriginMain) {
        git checkout -B main origin/main
    } else {
        # Check if local branch 'main' exists
        git rev-parse --verify main 2>$null
        if ($LASTEXITCODE -ne 0) {
            # If no commits yet, create initial commit
            git rev-parse HEAD 2>$null
            if ($LASTEXITCODE -ne 0) {
                git add .
                git commit -m "Initial commit (relinked)"
            }
            git branch -M main
        }
        # Set upstream for future pushes
        git branch --set-upstream-to=origin/main main 2>$null
    }

    Pop-Location
    Write-Host "✓ Processed $name"
}

Write-Host "`nDone."
