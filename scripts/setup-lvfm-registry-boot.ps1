#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$PythonExecutable = "python",
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ApiBase = "http://127.0.0.1:8000",
    [switch]$PublishRegistry,
    [switch]$StartApiIfDown,
    [double]$RegistryThreshold = -0.1,
    [int]$IntervalSeconds = 0,
    [switch]$CreateStartupLink,
    [string]$StartupShortcutName = "SeCuReDmE-LVFM-Bootstrap.cmd",
    [string]$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    [switch]$UseTaskScheduler,
    [string]$TaskName = "SeCuReDmE-LVFM-Bootstrap",
    [switch]$WriteRunKey,
    [string]$RunKeyName = "SeCuReDmE-LVFM-Bootstrap"
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path $RepoRoot).Path
$bootstrap = Join-Path $root "scripts\lvfm_windows_bootstrap.py"
$logDir = Join-Path $root "output"
$logFile = Join-Path $logDir "lvfm_bootstrap_watch.log"
New-Item -Path $logDir -ItemType Directory -Force | Out-Null

function Expand-CommandArgument {
    param([string]$Value)
    return '"' + $Value + '"'
}

$windowLauncher = Join-Path $root "scripts\lvfm_bootstrap_window.cmd"
if (!(Test-Path -LiteralPath $windowLauncher)) {
    throw "Window launcher missing: $windowLauncher"
}

if ($CreateStartupLink) {
    $startupPath = Join-Path $StartupFolder $StartupShortcutName
    Copy-Item -LiteralPath $windowLauncher -Destination $startupPath -Force
    Write-Host "Startup link updated: $startupPath"
}

$publishFlag = ""
if ($PublishRegistry) {
    $publishFlag = "--publish-registry"
}

$intervalArg = if ($IntervalSeconds -gt 0) { "--interval-seconds $IntervalSeconds" } else { "" }
$startApiArg = if ($StartApiIfDown) { "--start-api-if-down" } else { "" }
$thresholdArg = "--registry-threshold $RegistryThreshold"
$bootstrapArgs = "$(Expand-CommandArgument $bootstrap) --api-base $(Expand-CommandArgument $ApiBase) $publishFlag $intervalArg $startApiArg $thresholdArg --output-path $(Expand-CommandArgument $logFile) --run-once"
$pythonCmd = "$PythonExecutable $bootstrapArgs"

Write-Host "Launcher: $windowLauncher"
Write-Host "Command:"
Write-Host $pythonCmd

$registryBase = "HKCU:\Software\SeCuReDmE\LVFM"
$launcherSubKey = Join-Path $registryBase "Launcher"
if (!(Test-Path -Path $registryBase)) {
    New-Item -Path $registryBase -Force | Out-Null
}
New-Item -Path $launcherSubKey -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "RepositoryRoot" -PropertyType String -Value $root -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "LauncherPath" -PropertyType String -Value $windowLauncher -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "LogPath" -PropertyType String -Value $logFile -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "ApiBase" -PropertyType String -Value $ApiBase -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "PublishRegistry" -PropertyType String -Value ([string]$PublishRegistry.IsPresent) -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "StartApiIfDown" -PropertyType String -Value ([string]$StartApiIfDown.IsPresent) -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "RegistryThreshold" -PropertyType String -Value $RegistryThreshold -Force | Out-Null
New-ItemProperty -Path $launcherSubKey -Name "LastConfiguredUtc" -PropertyType String -Value (Get-Date).ToUniversalTime().ToString("o") -Force | Out-Null

if ($WriteRunKey) {
    $runValue = "`"$windowLauncher`""
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name $RunKeyName -Value $runValue -Force
    Write-Host "Run key configured: HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\$RunKeyName"
}

if (-not $UseTaskScheduler) {
    Write-Host "Setup complete (startup launcher only)."
    return
}

Write-Host "Registering scheduled task entry: $TaskName"

$action = New-ScheduledTaskAction -Execute $PythonExecutable -Argument $bootstrapArgs
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "FNP-QNN LVFM gate bootstrap and Windows register anchor." `
    -Force | Out-Null

Write-Host "Task registered: $TaskName"
