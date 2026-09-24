[CmdletBinding()]
param(
    [string]$DataDir = '',
    [string]$TargetConfig = '',
    [string]$BootstrapSecret = '',
    [switch]$LabFixtures
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if ($LabFixtures -and $TargetConfig) { throw 'Choose -LabFixtures or -TargetConfig, not both.' }
if (!$DataDir) { $DataDir = Join-Path $projectRoot 'var' }
$DataDir = [IO.Path]::GetFullPath($DataDir, $projectRoot)
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Install the service in .venv first; see README.md.' }
if (!(Test-Path -LiteralPath (Join-Path $projectRoot 'apps\web\dist\index.html'))) {
    throw 'Build the UI first: cd apps/web; npm ci; npm run build'
}
$healthUrl = 'http://127.0.0.1:8080/api/healthz'
$existingHealth = $null
try { $existingHealth = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2 } catch { }
if ($existingHealth -and $existingHealth.service -eq 'boundarylab') {
    Write-Output 'BoundaryLab is already running at http://127.0.0.1:8080. Existing mode and data directory were kept.'
    return
}

New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
$serverArgs = @('-u', '-m', 'boundarylab.devserver', '--data-dir', ('"' + $DataDir + '"'))
if ($LabFixtures) { $serverArgs += '--with-lab-fixtures' }
if ($TargetConfig) {
    $resolvedConfig = (Resolve-Path -LiteralPath $TargetConfig).Path
    $serverArgs += @('--target-config', ('"' + $resolvedConfig + '"'))
}
$previousSecret = $env:BOUNDARYLAB_BOOTSTRAP_SECRET
$configuredSecret = if ($BootstrapSecret) { $BootstrapSecret } else { $previousSecret }
$generatedSecret = !$configuredSecret
if ($generatedSecret) {
    $randomBytes = New-Object byte[] 24
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($randomBytes) } finally { $rng.Dispose() }
    $env:BOUNDARYLAB_BOOTSTRAP_SECRET = [Convert]::ToBase64String($randomBytes)
} else {
    $env:BOUNDARYLAB_BOOTSTRAP_SECRET = $configuredSecret
}
if ($env:BOUNDARYLAB_BOOTSTRAP_SECRET.Length -lt 16) { throw 'BOUNDARYLAB_BOOTSTRAP_SECRET must be at least 16 characters.' }
$launchId = [guid]::NewGuid().ToString('N')
$stdoutPath = Join-Path $DataDir "server-$launchId.out.log"
$stderrPath = Join-Path $DataDir "server-$launchId.err.log"
try {
    $serverProcess = Start-Process -FilePath $pythonPath -ArgumentList $serverArgs -WorkingDirectory $projectRoot `
        -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    do {
        $serverProcess.Refresh()
        if ($serverProcess.HasExited) { throw "Server exited. Inspect $stderrPath" }
        try {
            $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 1
            if ($health.service -eq 'boundarylab') {
                @{ pid = $serverProcess.Id; data_dir = $DataDir; stdout = $stdoutPath; stderr = $stderrPath } |
                    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $DataDir 'local-server.json')
                Write-Output "BoundaryLab $($health.version) is ready at http://127.0.0.1:8080 (background process $($serverProcess.Id))."
                if ($generatedSecret) { Write-Output "Bootstrap secret (shown once): $env:BOUNDARYLAB_BOOTSTRAP_SECRET" }
                Write-Output "Logs: $stderrPath"
                return
            }
        } catch { }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Server did not become ready within 15 seconds. Inspect $stderrPath"
} finally {
    $env:BOUNDARYLAB_BOOTSTRAP_SECRET = $previousSecret
}
