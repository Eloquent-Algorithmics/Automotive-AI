if ($env:GITHUB_ACTIONS) {
  Write-Host "This script does not currently work in GitHub Actions. Please run azd up locally first to set up Microsoft Entra application registration."
  exit 0
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  # fallback to python3 if python not found
  $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

Start-Process -FilePath ($pythonCmd).Source -ArgumentList "./scripts/auth_init.py" -Wait -NoNewWindow
