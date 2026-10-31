# Puts the stock Evilnat 4.93 ps2_netemu.self back (Windows PowerShell or PowerShell 7).
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore_netemu.ps1 [-Ps3Host 192.168.0.169] [-BackupFile .\local_only\backups\ps2_netemu_bad3e45c_....self]
# Without -BackupFile it uses a saved copy whose sha256 is the stock one: first in local_only\backups,
# then the copies install_netemu.ps1 left on the console in /dev_hdd0/ps2netemudisc/netemu_backup/.
# The Buzz! Bridge restore keeps working too (its backups are the same stock file).
param(
  [string]$Ps3Host = '192.168.0.169',
  [string]$BackupFile
)
$ErrorActionPreference = 'Stop'
$stockHash = 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'   # Evilnat 4.93 netemu
$consoleBackupDir = '/dev_hdd0/ps2netemudisc/netemu_backup/'
function FileHash([string]$path) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($path)))).Replace('-', '').ToLowerInvariant() }
  finally { $sha.Dispose() }
}
$backupDir = Join-Path $PSScriptRoot '..\local_only\backups'
[void](New-Item -ItemType Directory -Force -Path $backupDir)
$backupDir = (Resolve-Path -LiteralPath $backupDir).Path

$src = $null
if ($BackupFile) {
  $src = (Resolve-Path -LiteralPath $BackupFile).Path
} else {
  foreach ($f in (Get-ChildItem -LiteralPath $backupDir -Filter '*.self' | Sort-Object Name)) {
    if ((FileHash $f.FullName) -eq $stockHash) { $src = $f.FullName; break }
  }
  if (-not $src) {
    Write-Host 'No local copy of the stock netemu found; looking on the console disk...'
    $list = & curl.exe --silent --max-time 30 --list-only "ftp://$Ps3Host$consoleBackupDir" 2>$null
    foreach ($n in ($list | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^ps2_netemu_.*\.self$' } | Sort-Object)) {
      $got = Join-Path $backupDir ("_console_" + $n)
      curl.exe --fail --silent --show-error --max-time 120 -o $got "ftp://$Ps3Host$consoleBackupDir$n"
      if ($LASTEXITCODE -eq 0 -and (FileHash $got) -eq $stockHash) { $src = $got; break }
    }
  }
  if (-not $src) { throw 'No saved copy of the stock netemu was found. Pass one explicitly with -BackupFile (sha256 bad3e45c...c80a), or use the Buzz! Bridge restore.' }
}
$want = FileHash $src
Write-Host "Restoring: $src"
Write-Host "  sha256 $want"
if ($want -ne $stockHash) { Write-Warning 'This file is not the known stock netemu.' }

# Keep what is on the console now, then write.
$tmp = Join-Path $backupDir '_reading.self'
curl.exe --fail --silent --show-error --max-time 120 -o $tmp "ftp://$Ps3Host/dev_flash/ps2emu/ps2_netemu.self"
if ($LASTEXITCODE -ne 0) { throw "Could not read the current netemu from ftp://$Ps3Host/. Is the PS3 on, at the XMB, with webMAN MOD running? Nothing was changed." }
$currentHash = FileHash $tmp
$kept = Join-Path $backupDir ("ps2_netemu_{0}_{1}.self" -f $currentHash.Substring(0,8), (Get-Date -Format 'yyyyMMdd_HHmmss'))
Move-Item -LiteralPath $tmp -Destination $kept -Force
Write-Host "Current netemu saved to: $kept"
if ($currentHash -eq $want) { Write-Host 'That file is already installed. Nothing to do.'; return }

$verify = Join-Path $backupDir '_uploaded_check.self'
try {
  curl.exe --fail --silent --show-error -o NUL --max-time 20 "http://$Ps3Host/dev_blind?1"
  if ($LASTEXITCODE -ne 0) { throw 'Could not make dev_flash writable (CFW with webMAN MOD needed). Nothing was changed.' }
  curl.exe --fail --silent --show-error --max-time 120 -T $src "ftp://$Ps3Host/dev_blind/ps2emu/ps2_netemu.self"
  if ($LASTEXITCODE -ne 0) { throw 'Upload failed. Run this script again before starting any PS2 game.' }
  curl.exe --fail --silent --show-error --max-time 120 -o $verify "ftp://$Ps3Host/dev_blind/ps2emu/ps2_netemu.self"
  if ($LASTEXITCODE -ne 0 -or (FileHash $verify) -ne $want) { throw 'Read-back check failed. Run this script again before starting any PS2 game.' }
  Write-Host 'OK restored; file read back and verified.'
} finally {
  curl.exe --fail --silent --show-error -o NUL --max-time 20 "http://$Ps3Host/dev_blind?0"
  Remove-Item -LiteralPath $verify -Force -ErrorAction SilentlyContinue
}
Write-Host 'Done. The stock netemu is back; no restart is needed.'
