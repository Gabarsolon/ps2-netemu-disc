# Creates and uploads a 64 KiB zero-filled placeholder file to the PS3 HDD for durable netemu logging.
# Compatible with Windows PowerShell 5.1 and PowerShell 7+.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\make_log_placeholder.ps1 [-Ps3Host 192.168.0.169] [-Force]
#
# Target path on PS3: ftp://<Ps3Host>/dev_hdd0/tmp/netemu_log.bin (size: exactly 65536 bytes)
# Reads back and verifies size 65536 and all zeros.
# Never overwrites an existing non-zero file unless -Force is supplied.

[CmdletBinding()]
param(
  [string]$Ps3Host = '192.168.0.169',
  [string]$RemotePath = '/dev_hdd0/tmp/netemu_log.bin',
  [int]$FileSize = 65536,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "=== PS2 Netemu Log Placeholder Provisioning ==="
Write-Host "Target: ftp://$Ps3Host$RemotePath"
Write-Host "Size:   $FileSize bytes (64 KiB, 128 x 512-byte sectors)"

# Create a local scratch directory for placeholder creation and verification
$scratchDir = Join-Path $PSScriptRoot '..\local_only\tmp'
if (-not (Test-Path -LiteralPath $scratchDir)) {
  [void](New-Item -ItemType Directory -Force -Path $scratchDir)
}
$scratchDir = (Resolve-Path -LiteralPath $scratchDir).Path

$localPlaceholder = Join-Path $scratchDir 'placeholder_zeros_64k.bin'
$downloadCheck    = Join-Path $scratchDir '_placeholder_check.bin'

try {
  # 1. Check if the file already exists on the PS3
  Write-Host "Checking if $RemotePath already exists on PS3..."
  $checkOutput = Join-Path $scratchDir '_remote_probe.bin'
  if (Test-Path -LiteralPath $checkOutput) { Remove-Item -LiteralPath $checkOutput -Force }

  $probeSuccess = $false
  & curl.exe --fail --silent --show-error --max-time 15 -o $checkOutput "ftp://$Ps3Host$RemotePath" 2>$null
  if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $checkOutput)) {
    $existingBytes = [System.IO.File]::ReadAllBytes($checkOutput)
    $existingLen = $existingBytes.Length
    Write-Host "Remote file already exists (size: $existingLen bytes)."

    # Check if all zeros
    $isAllZeros = $true
    for ($i = 0; $i -lt $existingBytes.Length; $i++) {
      if ($existingBytes[$i] -ne 0) {
        $isAllZeros = $false
        break
      }
    }

    if ($existingLen -eq $FileSize -and $isAllZeros) {
      Write-Host "Existing remote file is already a valid $FileSize-byte zero-filled placeholder."
      Write-Host "No action required. Use -Force to re-upload."
      if (-not $Force) {
        return
      }
    } elseif (-not $isAllZeros -and -not $Force) {
      Write-Warning "Remote file contains non-zero data (may contain previous debug logs)!"
      Write-Warning "Refusing to overwrite without -Force. To inspect logs first, run tools\read_netemu_log.ps1."
      return
    }
  } else {
    Write-Host "Remote file does not exist yet. Proceeding with creation."
  }

  # 2. Generate local 65536 zero bytes
  Write-Host "Generating local 64 KiB zero-filled buffer..."
  $zeroBytes = New-Object byte[] $FileSize
  [System.IO.File]::WriteAllBytes($localPlaceholder, $zeroBytes)

  # 3. Upload to PS3 over FTP
  Write-Host "Uploading to ftp://$Ps3Host$RemotePath..."
  & curl.exe --fail --silent --show-error --max-time 30 --ftp-create-dirs -T $localPlaceholder "ftp://$Ps3Host$RemotePath"
  if ($LASTEXITCODE -ne 0) {
    throw "FTP upload to ftp://$Ps3Host$RemotePath failed with exit code $LASTEXITCODE."
  }
  Write-Host "Upload complete."

  # 4. Read back and verify size and contents
  Write-Host "Reading back from ftp://$Ps3Host$RemotePath for verification..."
  if (Test-Path -LiteralPath $downloadCheck) { Remove-Item -LiteralPath $downloadCheck -Force }
  & curl.exe --fail --silent --show-error --max-time 30 -o $downloadCheck "ftp://$Ps3Host$RemotePath"
  if ($LASTEXITCODE -ne 0) {
    throw "FTP download verification from ftp://$Ps3Host$RemotePath failed."
  }

  $verifyBytes = [System.IO.File]::ReadAllBytes($downloadCheck)
  if ($verifyBytes.Length -ne $FileSize) {
    throw "Verification failed: downloaded size is $($verifyBytes.Length) bytes, expected $FileSize bytes!"
  }

  for ($i = 0; $i -lt $verifyBytes.Length; $i++) {
    if ($verifyBytes[$i] -ne 0) {
      throw "Verification failed: non-zero byte found at offset 0x$($i.ToString('X4'))!"
    }
  }

  Write-Host "Verification SUCCESS: remote file is exactly $FileSize bytes and 100% zero-filled."
  Write-Host "Placeholder is ready for netemu durable logging at /dev_hdd0/tmp/netemu_log.bin."
}
finally {
  # Clean up temporary scratch files
  if (Test-Path -LiteralPath $localPlaceholder) { Remove-Item -LiteralPath $localPlaceholder -Force }
  if (Test-Path -LiteralPath $downloadCheck)    { Remove-Item -LiteralPath $downloadCheck -Force }
  if (Test-Path -LiteralPath $checkOutput)      { Remove-Item -LiteralPath $checkOutput -Force }
}
