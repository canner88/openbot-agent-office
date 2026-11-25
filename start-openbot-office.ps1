# Starts the Agent Office server and the OpenBot bridge if they are not already up.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Join-Path $env:USERPROFILE 'OpenBot\Shared\agent-office-live'
$node = (Get-Command node).Source
New-Item -ItemType Directory -Force -Path $project | Out-Null
$env:AGENT_OFFICE_PROJECT = $project

function OfficeUp {
  try {
    $r = Invoke-RestMethod -Uri 'http://127.0.0.1:4777/health' -TimeoutSec 2
    return [bool]$r.ok
  } catch { return $false }
}

if (-not (OfficeUp)) {
  Start-Process -FilePath $node -ArgumentList @('--experimental-sqlite', (Join-Path $root 'plugin\office\ctl.mjs'), 'start', $project) -WindowStyle Hidden -WorkingDirectory $project
  $i = 0
  while (-not (OfficeUp) -and $i -lt 30) { Start-Sleep -Milliseconds 400; $i++ }
}

$bridge = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" | Where-Object { $_.CommandLine -like '*openbot-bridge.mjs*' }
if (-not $bridge) {
  $out = Join-Path $env:TEMP 'agent-office-openbot-bridge.log'
  $err = Join-Path $env:TEMP 'agent-office-openbot-bridge.err.log'
  Start-Process -FilePath $node -ArgumentList @('--experimental-sqlite', (Join-Path $root 'plugin\office\openbot-bridge.mjs')) -WindowStyle Hidden -WorkingDirectory $project -RedirectStandardOutput $out -RedirectStandardError $err
}
