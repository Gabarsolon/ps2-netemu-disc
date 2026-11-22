<#!
Keep only the isolated PS3 Bluetooth WSL backend alive. Never stop a process.
An existing keeper is reused only after PID, start-time and command verification.
No USB driver, sharing, console or smart-plug changes happen in this helper.
!#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ReceiptPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$KeeperPurpose = 'Keep isolated PS3 Bluetooth backend alive'
$KeeperCommand = 'wsl -d PS3-Bluetooth -u root -- sleep infinity'

function Get-VerifiedKeeper {
    param([object]$Receipt)
    try {
        if ($Receipt.Purpose -ne $KeeperPurpose) { return $null }
        $KeeperId = [int]$Receipt.Pid
        if ($KeeperId -le 0) { return $null }
        $KeeperProcess = Get-Process -Id $KeeperId -ErrorAction Stop
        if ($KeeperProcess.ProcessName -ne 'wsl') { return $null }
        $ActualStart = $KeeperProcess.StartTime.ToUniversalTime()
        $ExpectedStart = [DateTime]::Parse([string]$Receipt.StartedUtc).ToUniversalTime()
        # Older receipt records were written immediately after process spawn.
        if ([Math]::Abs(($ActualStart - $ExpectedStart).TotalSeconds) -gt 5) { return $null }
        if ($Receipt.PSObject.Properties.Name -contains 'ProcessStartTimeUtc') {
            $RecordedStart = [DateTime]::Parse([string]$Receipt.ProcessStartTimeUtc).ToUniversalTime()
            if ($ActualStart.Ticks -ne $RecordedStart.Ticks) { return $null }
        }
        $ProcessInfo = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $KeeperId)
        $ExpectedTail = '(?i)(?:^|\s)-d\s+"?PS3-Bluetooth"?\s+-u\s+"?root"?\s+--\s+"?sleep"?\s+"?infinity"?\s*$'
        if (-not $ProcessInfo -or $ProcessInfo.CommandLine -notmatch $ExpectedTail) { return $null }
        if ($KeeperProcess.HasExited) { return $null }
        return $KeeperProcess
    }
    catch { return $null }
}

try {
    $ResolvedReceipt = [IO.Path]::GetFullPath($ReceiptPath)
    $ReceiptFolder = [IO.Path]::GetDirectoryName($ResolvedReceipt)
    [IO.Directory]::CreateDirectory($ReceiptFolder) | Out-Null
    $KeeperProcess = $null
    if (Test-Path -LiteralPath $ResolvedReceipt -PathType Leaf) {
        try {
            $PriorReceipt = Get-Content -LiteralPath $ResolvedReceipt -Raw | ConvertFrom-Json
            $KeeperProcess = Get-VerifiedKeeper $PriorReceipt
        }
        catch { $KeeperProcess = $null }
    }
    $Reused = $null -ne $KeeperProcess
    if (-not $Reused) {
        $WslExecutable = Join-Path $env:SystemRoot 'System32\wsl.exe'
        $KeeperProcess = Start-Process -FilePath $WslExecutable -ArgumentList @(
            '-d', 'PS3-Bluetooth', '-u', 'root', '--', 'sleep', 'infinity'
        ) -WindowStyle Hidden -PassThru
        Start-Sleep -Milliseconds 200
        $KeeperProcess.Refresh()
        if ($KeeperProcess.HasExited) { throw 'Isolated WSL keeper exited immediately.' }
    }
    $KeeperStart = $KeeperProcess.StartTime.ToUniversalTime().ToString('o')
    $NewReceipt = [ordered]@{
        StartedUtc = $KeeperStart
        ProcessStartTimeUtc = $KeeperStart
        Pid = $KeeperProcess.Id
        Purpose = $KeeperPurpose
        Command = $KeeperCommand
    }
    $TemporaryReceipt = Join-Path $ReceiptFolder ('bt_wsl_keeper.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $NewReceipt | ConvertTo-Json | Set-Content -LiteralPath $TemporaryReceipt -Encoding UTF8
    Move-Item -LiteralPath $TemporaryReceipt -Destination $ResolvedReceipt -Force
    [ordered]@{ KeeperPid = $KeeperProcess.Id; Reused = $Reused } | ConvertTo-Json -Compress
}
catch {
    Write-Error ('Bluetooth backend keeper failed: ' + $_.Exception.Message)
    exit 1
}
