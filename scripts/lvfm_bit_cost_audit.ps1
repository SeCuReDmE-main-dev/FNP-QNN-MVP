#requires -Version 5.1
param(
    [string]$GateSubKey = "HKCU:\\Software\\SeCuReDmE\\LVFM",
    [string]$RunKeyName = "SeCuReDmE-LVFM-Bootstrap",
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -Path $GateSubKey)) {
    Write-Host "Gate registry key not found: $GateSubKey"
    exit 1
}

if (-not (Get-ItemProperty -Path $GateSubKey -Name RegistryPayloadJson -ErrorAction SilentlyContinue)) {
    Write-Host "RegistryPayloadJson missing from $GateSubKey"
    exit 1
}

$gateProps = Get-ItemProperty -Path $GateSubKey
$bitTable = @()
if ($gateProps.BitTableJson) {
    try {
        $bitTable = ($gateProps.BitTableJson | ConvertFrom-Json -ErrorAction Stop)
    } catch {
        Write-Host "Could not parse BitTableJson"
        exit 1
    }
}

$totalRegisterWeight = 0.0
$totalCost = 0.0
$ledger = @()

foreach ($bit in $bitTable) {
    $t = [double]$bit.T
    $i = [double]$bit.I
    $dF = [double]$bit.dF
    $f = [double]$bit.F
    $w = [double]$bit.register_weight
    $tiDf = ($t - $i + $dF)
    $cost = $w * ($i + $f + (1.0 - $t))
    $totalRegisterWeight += $w
    $totalCost += $cost
    $ledger += [PSCustomObject]@{
        node_id = $bit.node_id
        t = [math]::Round($t, 6)
        i = [math]::Round($i, 6)
        dF = [math]::Round($dF, 6)
        f = [math]::Round($f, 6)
        register_weight = $w
        metadata = $bit.metadata
        ti_df = [math]::Round($tiDf, 6)
        cost = [math]::Round($cost, 6)
    }
}

$orderedLedger = $ledger | Sort-Object -Property cost -Descending
$snapshot = [ordered]@{
    gate_id = $gateProps.GateId
    verdict = $gateProps.Verdict
    lock_state = $gateProps.LockState
    lock_reason = $gateProps.LockReason
    ti_df_raw = $gateProps.TiDfRaw
    lock_score = $gateProps.LockScore
    total_bits = $orderedLedger.Count
    total_register_weight = [math]::Round($totalRegisterWeight, 6)
    total_cost = [math]::Round($totalCost, 6)
    run_key_present = $false
    run_key_value = $null
    bits = $orderedLedger
}

try {
    $runValue = Get-ItemPropertyValue -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name $RunKeyName -ErrorAction Stop
    if ($runValue) {
        $snapshot.run_key_present = $true
        $snapshot.run_key_value = $runValue
    }
} catch {
    $snapshot.run_key_present = $false
}

if ($AsJson) {
    $snapshot | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "LVFM Bit Cost Audit"
Write-Host "GateId=$($snapshot.gate_id)"
Write-Host "Verdict=$($snapshot.verdict)"
Write-Host "LockState=$($snapshot.lock_state)"
Write-Host "TiDfRaw=$($snapshot.ti_df_raw)"
Write-Host "LockScore=$($snapshot.lock_score)"
Write-Host "TotalBits=$($snapshot.total_bits)"
Write-Host "TotalRegisterWeight=$($snapshot.total_register_weight)"
Write-Host "TotalCost=$($snapshot.total_cost)"
Write-Host "RunKey=$RunKeyName present=$($snapshot.run_key_present)"

Write-Host "TopCostBits:"
foreach ($row in $orderedLedger) {
    $label = if ($row.metadata -and $row.metadata.label) { $row.metadata.label } else { "" }
    $src = if ($row.metadata -and $row.metadata.source) { $row.metadata.source } else { "" }
    Write-Host ("  {0} label={1} source={2} T={3} I={4} dF={5} F={6} w={7} cost={8} tiDf={9}" -f `
        $row.node_id, $label, $src, $row.t, $row.i, $row.dF, $row.f, $row.register_weight, $row.cost, $row.ti_df)
}
