import subprocess, sys

ps_code = '''
$p1 = 'C:\\Users\\remus\\ps2-netemu-disc\\tools\\make_log_placeholder.ps1'
$p2 = 'C:\\Users\\remus\\ps2-netemu-disc\\tools\\read_netemu_log.ps1'
$p3 = 'C:\\Users\\remus\\ps2-netemu-disc\\tools\\install_netemu.ps1'
$p4 = 'C:\\Users\\remus\\ps2-netemu-disc\\tools\\restore_netemu.ps1'

foreach ($p in @($p1, $p2, $p3, $p4)) {
    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$tokens, [ref]$errors)
    if ($errors.Count -eq 0) {
        Write-Host "$([System.IO.Path]::GetFileName($p)): PARSE SUCCESS (0 errors)"
    } else {
        Write-Host "$([System.IO.Path]::GetFileName($p)): PARSE ERRORS: $($errors.Count)"
        foreach ($e in $errors) {
            Write-Host "  $e"
        }
    }
}
'''

res = subprocess.run(['powershell', '-NoProfile', '-Command', ps_code], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
sys.exit(res.returncode)
