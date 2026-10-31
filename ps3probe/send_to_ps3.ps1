# OWNER RUNS THIS EXPLICITLY. Uploads app PKG to HDD only, never installs/launches.
# The agent must only parse-check this script, never execute it.
param([string]$Ps3Host = '192.168.0.169')
$ErrorActionPreference = 'Stop'
function Get-ProbeSha256([string]$Path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $sha.ComputeHash([System.IO.File]::ReadAllBytes($Path))
        return [BitConverter]::ToString($digest).Replace('-', '').ToLowerInvariant()
    } finally { $sha.Dispose() }
}
$repo = Split-Path $PSScriptRoot -Parent
$output = Join-Path $repo 'local_only\ps3probe'
$pkg = Join-Path $output 'PS2DiscProbe.pkg'
$manifestPath = Join-Path $output 'package_manifest.json'
if (-not (Test-Path -LiteralPath $pkg)) { throw "Missing package: $pkg" }
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$want = Get-ProbeSha256 $pkg
if ($manifest.package -ne 'PS2DiscProbe.pkg' -or $manifest.sha256 -ne $want) { throw 'Package/manifest mismatch' }
$remote = "ftp://$Ps3Host/dev_hdd0/packages/PS2DiscProbe.pkg"
Write-Host "Uploading PS2DiscProbe.pkg to the PS3 HDD: $Ps3Host"
& curl.exe --fail --silent --show-error --ftp-create-dirs --connect-timeout 10 --max-time 120 -T $pkg $remote
if ($LASTEXITCODE) { throw 'Upload failed' }
$back = Join-Path $output ('readback-' + [guid]::NewGuid().ToString('N') + '.pkg')
try {
    & curl.exe --fail --silent --show-error --connect-timeout 10 --max-time 120 -o $back $remote
    if ($LASTEXITCODE) { throw 'Read-back failed' }
    $actual = Get-ProbeSha256 $back
    if ($actual -ne $want) { throw 'Uploaded package hash mismatch' }
} finally {
    Remove-Item -LiteralPath $back -Force -ErrorAction SilentlyContinue
}
Write-Host "Verified SHA256: $want"
Write-Host 'On the PS3, install PS2DiscProbe.pkg with Package Manager, then follow ps3probe/README.md.'
