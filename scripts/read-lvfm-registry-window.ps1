#requires -Version 5.1
param(
    [string]$RegistrySubKey = "HKCU:\\Software\\SeCuReDmE\\LVFM\\Launcher",
    [string]$GateSubKey = "HKCU:\\Software\\SeCuReDmE\\LVFM",
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -Path $RegistrySubKey)) {
    Write-Host "Registry key not found: $RegistrySubKey"
    exit 1
}

$launcherProps = Get-ItemProperty -Path $RegistrySubKey
$snapshot = [ordered]@{
    window_key = $RegistrySubKey
    repository_root = $launcherProps.RepositoryRoot
    launcher_path = $launcherProps.LauncherPath
    log_path = $launcherProps.LogPath
    api_base = $launcherProps.ApiBase
    publish_registry = $launcherProps.PublishRegistry
    registry_threshold = $launcherProps.RegistryThreshold
    last_configured_utc = $launcherProps.LastConfiguredUtc
    gate = $null
}

if (-not $AsJson) {
    Write-Host "Reading launcher registry window key: $RegistrySubKey"
    Write-Host "RepositoryRoot=$($launcherProps.RepositoryRoot)"
    Write-Host "LauncherPath=$($launcherProps.LauncherPath)"
    Write-Host "LogPath=$($launcherProps.LogPath)"
    Write-Host "ApiBase=$($launcherProps.ApiBase)"
    Write-Host "PublishRegistry=$($launcherProps.PublishRegistry)"
    Write-Host "RegistryThreshold=$($launcherProps.RegistryThreshold)"
    Write-Host "LastConfiguredUtc=$($launcherProps.LastConfiguredUtc)"
}

if (Test-Path -Path $GateSubKey) {
    $gateProps = Get-ItemProperty -Path $GateSubKey
    $snapshot.gate = [ordered]@{
        gate_id = $gateProps.GateId
        verdict = $gateProps.Verdict
        lock_state = $gateProps.LockState
        lock_reason = $gateProps.LockReason
        sequence_fingerprint = $gateProps.SequenceFingerprint
        created_at = $gateProps.CreatedAt
        ti_df_raw = $gateProps.TiDfRaw
        lock_score_raw = $gateProps.LockScoreRaw
        lock_score = $gateProps.LockScore
        compact_json = $gateProps.CompactJson
        exact_bits_json = $gateProps.ExactBitsJson
        register_keys_json = $gateProps.RegisterKeysJson
        bit_table_json = $gateProps.BitTableJson
        registry_payload_json = $gateProps.RegistryPayloadJson
        registry_schema_version = $gateProps.RegistrySchemaVersion
        history_event_id = $gateProps.HistoryEventId
        history_path = $gateProps.HistoryPath
        history_written_at = $gateProps.HistoryWrittenAt
        trace_line = $gateProps.TraceLine
    }

    if (-not $AsJson) {
        Write-Host "GateSummary:"
        Write-Host "  GateId=$($gateProps.GateId)"
        Write-Host "  Verdict=$($gateProps.Verdict)"
        Write-Host "  LockState=$($gateProps.LockState)"
        Write-Host "  LockReason=$($gateProps.LockReason)"
        Write-Host "  TiDfRaw=$($gateProps.TiDfRaw)"
        Write-Host "  LockScoreRaw=$($gateProps.LockScoreRaw)"
        Write-Host "  CreatedAt=$($gateProps.CreatedAt)"
        if ($gateProps.RegistrySchemaVersion) {
            Write-Host "  RegistrySchemaVersion=$($gateProps.RegistrySchemaVersion)"
        }
        if ($gateProps.HistoryEventId) {
            Write-Host "  HistoryEventId=$($gateProps.HistoryEventId)"
        }
        if ($gateProps.HistoryPath) {
            Write-Host "  HistoryPath=$($gateProps.HistoryPath)"
        }
        if ($gateProps.HistoryWrittenAt) {
            Write-Host "  HistoryWrittenAt=$($gateProps.HistoryWrittenAt)"
        }
        if ($gateProps.ExactBitsJson) {
            Write-Host "  ExactBitsJsonLen=$($gateProps.ExactBitsJson.Length)"
        }
        if ($gateProps.BitTableJson) {
            Write-Host "  BitTableJsonLen=$($gateProps.BitTableJson.Length)"
        }
        if ($gateProps.RegistryPayloadJson) {
            Write-Host "  RegistryPayloadJsonLen=$($gateProps.RegistryPayloadJson.Length)"
        }
        if ($gateProps.TraceLine) {
            Write-Host "  TraceLine=$($gateProps.TraceLine)"
        }
    }
}

if ($AsJson) {
    $snapshot | ConvertTo-Json -Depth 10
} else {
    Write-Host "Complete"
}
