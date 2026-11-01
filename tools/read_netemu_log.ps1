# Reads and decodes the netemu durable debug log from the PS3 HDD over FTP.
# Compatible with Windows PowerShell 5.1 and PowerShell 7+.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\read_netemu_log.ps1 [-Ps3Host 192.168.0.169] [-OutFile .\local_only\last_log.bin]
#
# Connects read-only over FTP. Does NOT write to the console.

[CmdletBinding()]
param(
  [string]$Ps3Host = '192.168.0.169',
  [string]$RemotePath = '/dev_hdd0/tmp/netemu_log.bin',
  [string]$OutFile = ''
)

$ErrorActionPreference = 'Stop'

Write-Host "=== PS2 Netemu Debug Log Reader ==="
Write-Host "Source: ftp://$Ps3Host$RemotePath"

# Scratch directory
$scratchDir = Join-Path $PSScriptRoot '..\local_only\tmp'
if (-not (Test-Path -LiteralPath $scratchDir)) {
  [void](New-Item -ItemType Directory -Force -Path $scratchDir)
}
$scratchDir = (Resolve-Path -LiteralPath $scratchDir).Path

$tempDownload = Join-Path $scratchDir '_download_log.bin'

try {
  Write-Host "Downloading log file from PS3..."
  if (Test-Path -LiteralPath $tempDownload) { Remove-Item -LiteralPath $tempDownload -Force }
  & curl.exe --fail --silent --show-error --max-time 30 -o $tempDownload "ftp://$Ps3Host$RemotePath"
  if ($LASTEXITCODE -ne 0) {
    throw "FTP download from ftp://$Ps3Host$RemotePath failed with exit code $LASTEXITCODE. Is the PS3 running webMAN MOD FTP?"
  }

  $bytes = [System.IO.File]::ReadAllBytes($tempDownload)
  $len = $bytes.Length
  Write-Host "Downloaded $len bytes."

  if ($OutFile -ne '') {
    [System.IO.File]::WriteAllBytes($OutFile, $bytes)
    Write-Host "Saved copy to $OutFile"
  }

  if ($len -lt 512) {
    throw "File is too small to contain even a single sector ($len bytes)."
  }

  # Helper functions for big-endian decoding
  function Get-U16BE([byte[]]$b, [int]$off) {
    return [uint16](($b[$off] -shl 8) -bor $b[$off + 1])
  }
  function Get-U32BE([byte[]]$b, [int]$off) {
    return [uint32](($b[$off] -shl 24) -bor ($b[$off + 1] -shl 16) -bor ($b[$off + 2] -shl 8) -bor $b[$off + 3])
  }
  function Get-U64BE([byte[]]$b, [int]$off) {
    $hi = [uint64](Get-U32BE $b $off)
    $lo = [uint64](Get-U32BE $b ($off + 4))
    return [uint64](($hi -shl 32) -bor $lo)
  }
  function Get-Ascii([byte[]]$b, [int]$off, [int]$count) {
    $sub = New-Object byte[] $count
    [System.Array]::Copy($b, $off, $sub, 0, $count)
    # Stop at first null
    $nullIdx = [System.Array]::IndexOf($sub, [byte]0)
    if ($nullIdx -ge 0) {
      return [System.Text.Encoding]::ASCII.GetString($sub, 0, $nullIdx)
    }
    return [System.Text.Encoding]::ASCII.GetString($sub)
  }

  # Check if all zeros
  $isAllZeros = $true
  for ($i = 0; $i -lt $len; $i++) {
    if ($bytes[$i] -ne 0) { $isAllZeros = $false; break }
  }

  if ($isAllZeros) {
    Write-Host ""
    Write-Host "Log file is completely blank (all $len bytes are zeros)."
    Write-Host "The placeholder exists, but no netemu log records have been written to it yet."
    return
  }

  # Sector 0: Header
  Write-Host ""
  Write-Host "--- LOG HEADER (Sector 0) ---"
  $hdrMagic = Get-Ascii $bytes 0 8
  Write-Host "Header Magic: '$hdrMagic'"

  if ($hdrMagic -eq 'NETEMULG') {
    $version  = Get-U32BE $bytes 8
    $hdrSize  = Get-U32BE $bytes 12
    $fileSize = Get-U32BE $bytes 16
    $secSize  = Get-U32BE $bytes 20
    $maxRec   = Get-U32BE $bytes 24
    $nextIdx  = Get-U32BE $bytes 28
    $bootTb   = Get-U64BE $bytes 32
    $clean    = Get-U32BE $bytes 40
    $recCount = Get-U32BE $bytes 44

    Write-Host "Version:      0x$($version.ToString('X8'))"
    Write-Host "Header Size:  $hdrSize bytes"
    Write-Host "File Size:    $fileSize bytes"
    Write-Host "Sector Size:  $secSize bytes"
    Write-Host "Capacity:     $maxRec records"
    Write-Host "Next Record:  #$nextIdx"
    Write-Host "Boot TB:      0x$($bootTb.ToString('X16')) ($bootTb ticks)"
    $shutdownStatus = if ($clean -eq 1) { 'CLEAN' } else { 'UNCOMMITTED / CRASH' }
    Write-Host "Shutdown:     $shutdownStatus"
    Write-Host "Record Count: $recCount"
  } else {
    Write-Warning "Header magic does not match 'NETEMULG' (found '$hdrMagic')."
  }

  # Parse records (Sector 1 onwards, each 512 bytes)
  $sectorCount = [int]($len / 512)
  $records = New-Object System.Collections.Generic.List[Object]
  Write-Host ""
  Write-Host "--- LOG RECORDS ---"

  for ($s = 1; $s -lt $sectorCount; $s++) {
    $off = $s * 512
    # Check if sector is all zeros
    $secZero = $true
    for ($k = 0; $k -lt 512; $k++) {
      if ($bytes[$off + $k] -ne 0) { $secZero = $false; break }
    }
    if ($secZero) { continue }

    $recMagic = Get-Ascii $bytes $off 4
    if ($recMagic -eq 'LOGR') {
      $seq    = Get-U32BE $bytes ($off + 4)
      $tag    = Get-U32BE $bytes ($off + 8)
      $flags  = Get-U32BE $bytes ($off + 12)
      $tb     = Get-U64BE $bytes ($off + 16)
      $valA   = Get-U64BE $bytes ($off + 24)
      $valB   = Get-U64BE $bytes ($off + 32)
      $bootId = Get-U64BE $bytes ($off + 40)
      $text   = Get-Ascii $bytes ($off + 72) (512 - 72)

      $tagBytes = @($bytes[$off + 8], $bytes[$off + 9], $bytes[$off + 10], $bytes[$off + 11])
      $isTagAscii = $true
      foreach ($tByte in $tagBytes) {
        if ($tByte -lt 32 -or $tByte -gt 126) { $isTagAscii = $false; break }
      }
      $tagStr = if ($isTagAscii) { "'" + [System.Text.Encoding]::ASCII.GetString($tagBytes) + "'" } else { "0x" + $tag.ToString('X8') }

      $isCurrent = if ($bootTb -ne 0) { ($bootId -eq $bootTb) } else { $true }

      $rec = [PSCustomObject]@{
        Sector     = $s
        Seq        = $seq
        Tag        = $tag
        TagStr     = $tagStr
        Flags      = $flags
        TB         = $tb
        ValA       = $valA
        ValB       = $valB
        BootId     = $bootId
        IsCurrent  = $isCurrent
        Text       = $text
        CrashPoint = $false
      }
      $records.Add($rec)
    } else {
      # Unstructured sector dump
      $sample = [System.BitConverter]::ToString($bytes, $off, 32).Replace('-', ' ')
      $rec = [PSCustomObject]@{
        Sector    = $s
        RawMagic  = $recMagic
        RawHex    = $sample
      }
      $records.Add($rec)
    }
  }

  # Crash point analysis on WAL records
  $TAG_PRE  = 0x50524520  # 'PRE '
  $TAG_POST = 0x504F5354  # 'POST'
  $TAG_TMO  = 0x544D4F20  # 'TMO '
  $TAG_END  = 0x454E4420  # 'END '

  $pendingPre = $null
  foreach ($r in $records) {
    if ($null -ne $r.Tag -and $r.IsCurrent) {
      if ($r.Tag -eq $TAG_PRE) {
        if ($null -ne $pendingPre) {
          $pendingPre.CrashPoint = $true
        }
        $pendingPre = $r
      } elseif ($r.Tag -eq $TAG_POST) {
        $pendingPre = $null
      } elseif ($r.Tag -eq $TAG_TMO -or $r.Tag -eq $TAG_END) {
        $pendingPre = $null
      }
    }
  }
  if ($null -ne $pendingPre) {
    $pendingPre.CrashPoint = $true
  }

  $crashFound = $null
  foreach ($r in $records) {
    if ($null -ne $r.Tag) {
      $notes = New-Object System.Collections.Generic.List[string]
      if (-not $r.IsCurrent) {
        $notes.Add(("[STALE boot_id=0x{0:X16}]" -f $r.BootId))
      }
      if ($r.CrashPoint) {
        $notes.Add("[CRASH POINT]")
        $crashFound = $r
      }
      $noteStr = if ($notes.Count -gt 0) { " " + ($notes -join " ") } else { "" }
      Write-Host ("[Sector {0:D3}] Seq={1:D4} Tag={2} BootID=0x{3:X16} TB=0x{4:X16} A=0x{5:X16} B=0x{6:X16} -> {7}{8}" -f $r.Sector, $r.Seq, $r.TagStr, $r.BootId, $r.TB, $r.ValA, $r.ValB, $r.Text, $noteStr)
    } else {
      Write-Host ("[Sector {0:D3}] Raw (Magic '{1}'): {2} ..." -f $r.Sector, $r.RawMagic, $r.RawHex)
    }
  }

  Write-Host ""
  Write-Host "Total populated log records found: $($records.Count)"
  if ($null -ne $crashFound) {
    Write-Host ""
    Write-Host "*** [CRASH POINT DETECTED] ***" -ForegroundColor Red
    Write-Host ("Execution halted during call logged at Sector {0} (Seq={1}):" -f $crashFound.Sector, $crashFound.Seq)
    Write-Host ("  Command / Step : {0}" -f $crashFound.Text)
    Write-Host ("  Timestamp (TB) : 0x{0:X16}" -f $crashFound.TB)
    Write-Host ("  Parameters     : A=0x{0:X16}, B=0x{1:X16}" -f $crashFound.ValA, $crashFound.ValB)
  }
}
finally {
  if (Test-Path -LiteralPath $tempDownload) { Remove-Item -LiteralPath $tempDownload -Force }
}
