# Installs any ps2_netemu.self build of this project on a CFW PS3 (Windows PowerShell or PowerShell 7).
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\ps2_netemu_probe1.self [-Ps3Host 192.168.0.169] [-Force]
# The PS3 must be at the XMB with webMAN MOD running (its FTP and web server). curl.exe ships with Windows 10/11.
# Order: read the current file and keep it (PC + console disk) -> write -> read back and compare -> always unmount dev_blind.
# Run tools\restore_netemu.ps1 to put the stock file back.
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$File,
  [string]$Ps3Host = '192.168.0.169',
  [switch]$Force          # skip the question when the file currently on the console is not a known one
)
$ErrorActionPreference = 'Stop'
$stockHash  = 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'   # Evilnat 4.93 netemu
$buzzHash   = '74e890bf7f77edfd92d4c0a57f45e73cf7fe39aa3c21cd7587948fb3c81ade40'   # Buzz! Bridge v1.3.0 netemu
$knownHashes = @($stockHash, $buzzHash)
$consoleBackupDir = '/dev_hdd0/ps2netemudisc/netemu_backup/'

function FileHash([string]$path) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($path)))).Replace('-', '').ToLowerInvariant() }
  finally { $sha.Dispose() }
}

if (-not (Test-Path -LiteralPath $File)) { throw "File not found: $File" }
$src = (Resolve-Path -LiteralPath $File).Path
$targetHash = FileHash $src
Write-Host "Installing: $src"
Write-Host "  sha256 $targetHash"
if ((Get-Item -LiteralPath $src).Length -lt 1MB) { throw 'That file is too small to be a ps2_netemu.self. Nothing was changed.' }

$backupDir = Join-Path $PSScriptRoot '..\local_only\backups'
[void](New-Item -ItemType Directory -Force -Path $backupDir)
$backupDir = (Resolve-Path -LiteralPath $backupDir).Path

# 1. Read what is on the console now and keep it. Nothing is written yet.
$tmp = Join-Path $backupDir '_reading.self'
curl.exe --fail --silent --show-error --max-time 120 -o $tmp "ftp://$Ps3Host/dev_flash/ps2emu/ps2_netemu.self"
if ($LASTEXITCODE -ne 0) { throw "Could not read the current netemu from ftp://$Ps3Host/. Is the PS3 on, at the XMB, with webMAN MOD running? Nothing was changed." }
$currentHash = FileHash $tmp
$backup = Join-Path $backupDir ("ps2_netemu_{0}_{1}.self" -f $currentHash.Substring(0,8), (Get-Date -Format 'yyyyMMdd_HHmmss'))
Move-Item -LiteralPath $tmp -Destination $backup -Force
Write-Host "Current netemu saved to: $backup"
Write-Host "  sha256 $currentHash"

if ($currentHash -eq $targetHash) { Write-Host 'This netemu is already installed. Nothing to do.'; return }

if ($knownHashes -notcontains $currentHash -and -not $Force) {
  Write-Host ''
  Write-Host 'The netemu on your console is not a known one (stock Evilnat 4.93 or the Buzz! Bridge v1.3.0 build).'
  Write-Host 'The backup above lets you put it back.'
  if ((Read-Host 'Type OVERWRITE to continue') -ne 'OVERWRITE') { Write-Host 'Cancelled. Nothing was changed.'; return }
}

# 2. Also keep a copy on the console's own disk.
curl.exe --fail --silent --show-error --max-time 120 --ftp-create-dirs -T $backup "ftp://$Ps3Host$consoleBackupDir$(Split-Path $backup -Leaf)"
if ($LASTEXITCODE -ne 0) { Write-Warning 'Could not copy the backup to the console disk. The copy on this computer is still there.' }

# 3. Overwrite, verify by reading it back, always unmount.
$verify = Join-Path $backupDir '_uploaded_check.self'
try {
  curl.exe --fail --silent --show-error -o NUL --max-time 20 "http://$Ps3Host/dev_blind?1"
  if ($LASTEXITCODE -ne 0) { throw 'Could not make dev_flash writable (CFW with webMAN MOD needed). Nothing was changed.' }
  curl.exe --fail --silent --show-error --max-time 120 -T $src "ftp://$Ps3Host/dev_blind/ps2emu/ps2_netemu.self"
  if ($LASTEXITCODE -ne 0) { throw 'Upload failed. Run tools\restore_netemu.ps1 before starting any PS2 game.' }
  curl.exe --fail --silent --show-error --max-time 120 -o $verify "ftp://$Ps3Host/dev_blind/ps2emu/ps2_netemu.self"
  if ($LASTEXITCODE -ne 0 -or (FileHash $verify) -ne $targetHash) { throw 'Read-back check failed. Run tools\restore_netemu.ps1 before starting any PS2 game.' }
  Write-Host 'OK installed; file read back and verified.'
} finally {
  curl.exe --fail --silent --show-error -o NUL --max-time 20 "http://$Ps3Host/dev_blind?0"
  Remove-Item -LiteralPath $verify -Force -ErrorAction SilentlyContinue
}
Write-Host 'Done. Start a PS2 game; no restart is needed.'
