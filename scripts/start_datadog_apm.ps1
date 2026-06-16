$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot
try {
  $ddtraceRun = Get-Command ddtrace-run -ErrorAction SilentlyContinue
  if (-not $ddtraceRun) {
    throw "ddtrace-run was not found. Run: pip install -r requirements.txt"
  }

  $commitSha = ""
  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git) {
    $commitSha = (git rev-parse HEAD 2>$null)
  }

  $env:DD_SERVICE = if ($env:DD_SERVICE) { $env:DD_SERVICE } else { "fnp-qnn-local-research-simulator" }
  $env:DD_ENV = if ($env:DD_ENV) { $env:DD_ENV } else { "local" }
  $env:DD_LOGS_INJECTION = if ($env:DD_LOGS_INJECTION) { $env:DD_LOGS_INJECTION } else { "true" }
  $env:DD_TRACE_SAMPLE_RATE = if ($env:DD_TRACE_SAMPLE_RATE) { $env:DD_TRACE_SAMPLE_RATE } else { "1" }
  $env:DD_PROFILING_ENABLED = if ($env:DD_PROFILING_ENABLED) { $env:DD_PROFILING_ENABLED } else { "true" }
  $env:DD_DATA_STREAMS_ENABLED = if ($env:DD_DATA_STREAMS_ENABLED) { $env:DD_DATA_STREAMS_ENABLED } else { "false" }
  $env:DD_TRACE_REMOVE_INTEGRATION_SERVICE_NAMES_ENABLED = if ($env:DD_TRACE_REMOVE_INTEGRATION_SERVICE_NAMES_ENABLED) { $env:DD_TRACE_REMOVE_INTEGRATION_SERVICE_NAMES_ENABLED } else { "true" }
  $env:DD_APPSEC_ENABLED = if ($env:DD_APPSEC_ENABLED) { $env:DD_APPSEC_ENABLED } else { "false" }
  $env:DD_IAST_ENABLED = if ($env:DD_IAST_ENABLED) { $env:DD_IAST_ENABLED } else { "false" }
  $env:DD_APPSEC_SCA_ENABLED = if ($env:DD_APPSEC_SCA_ENABLED) { $env:DD_APPSEC_SCA_ENABLED } else { "false" }
  $env:DD_GIT_REPOSITORY_URL = if ($env:DD_GIT_REPOSITORY_URL) { $env:DD_GIT_REPOSITORY_URL } else { "github.com/securedme-main-dev/fnp-qnn-mvp-version-disease-simulator-" }
  if ($commitSha) {
    $env:DD_GIT_COMMIT_SHA = $commitSha
  }

  ddtrace-run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
} finally {
  Pop-Location
}
