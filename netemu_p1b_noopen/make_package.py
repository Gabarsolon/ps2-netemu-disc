"""Prepare guarded installer sources and parse their AST; never execute them."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
H=Path(__file__).resolve().parent;P=H/'package';P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
template=(H/'dependencies/install_s4c3.ps1').read_text()
allowed=set();sources={}
folders=[*H.parent.glob('netemu_*'),H.parent/'raw_capture_debug3/package',H.parent/'raw_capture_debug5/package',H.parent/'raw_capture_debug6/package',H.parent/'raw_capture_debug7/package',H.parent/'raw_capture_debug8/package',H.parent/'raw_capture_debug9/package',H.parent/'raw_capture_debug10/package',
 Path(r'C:/Users/remus/AppData/Local/Temp/claude/C--Users-remus/bdee2a74-bc7e-4154-89d1-de522c5fd907/scratchpad/raw_capture_debug2/package')]
for folder in folders:
 for f in [*folder.glob('install_*.ps1'),*folder.glob('undo*.ps1')]:
  hashes={s.lower() for s in re.findall(r"['\"]([a-fA-F0-9]{64})['\"]",f.read_text())}
  allowed.update(hashes);sources[str(f)]=dict(sha256=sha(f),accepted_hashes=sorted(hashes))
 for f in folder.glob('*.self'):
  allowed.add(sha(f));sources[str(f)]=dict(sha256=sha(f))
allowed.update(re.findall(r"'([a-f0-9]{64})'",template))
required=['319a56c89911084295307bf5a6a87dc32f818c78603f2e01155dfffc81f8c1a9','3ffbe42d5f8d8cb43ea8a476358dfa9beeb7a2d199acf8e169f23942b63fa46e','58a89f02511ef133327d3d9cd94ee0a0ee681769129806fbcd7f62e39a724b02','55310a42f6a92f20f2b5adc62ce44f5fc50de09c4746d817770e3281b58d6511','9948c2e77a860d2e9e3bbc08f7fb9cdbe55b783b0312931e6f2d4a0b0fcd1242']
allowed.update(required)
original='bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'
for v in ['S4L3']:
 shutil.copyfile(H/f'ps2_netemu_{v}.self',P/f'ps2_netemu_{v}.self');allowed.add(sha(P/f'ps2_netemu_{v}.self'))
shutil.copyfile(H/'dependencies/original.self',P/'ps2_netemu_original.self');assert sha(P/'ps2_netemu_original.self')==original
allowed.add(original)
for v in ['S4L3','original']:
 digest=sha(P/f'ps2_netemu_{v}.self')
 t=template.replace('S4C3',v).replace('s4c3',v.lower()).replace('55310a42f6a92f20f2b5adc62ce44f5fc50de09c4746d817770e3281b58d6511',digest)
 t=re.sub(r'\$allowed = @\(.*?\n\)',"$allowed = @(\n"+''.join("  '"+x+"'\n" for x in sorted(allowed))+')',t,flags=re.S)
 name='undo_restore_original.ps1' if v=='original' else f'install_{v.lower()}.ps1'
 (P/name).write_text(t)
 assert t.index('Unknown current emulator hash')<t.index('http://$Ps3Host/dev_blind?1')<t.index('-T $src')
 assert t.index('FileHash $src')<t.index('curl.exe') and 'FileHash $verify' in t and '} finally {' in t
 assert 'dev_flash/ps2emu/ps2_netemu.self' in t and '-T $src "ftp://$Ps3Host/dev_blind/' in t
 assert not re.search(r'-T .*dev_flash',t)
code="$rows=foreach($f in Get-ChildItem -LiteralPath $PWD -Filter '*.ps1'){$t=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName,[ref]$t,[ref]$e);if($e.Count){throw ($e|Out-String)};[pscustomobject]@{file=$f.Name;parsed=$true;executed=$false}};ConvertTo-Json -InputObject @($rows)"
r=subprocess.run(['powershell.exe','-NoProfile','-Command',code],cwd=P,capture_output=True,text=True,check=True)
(H/'evidence/installer_parse.json').write_text(json.dumps(dict(passed=True,scripts=json.loads(r.stdout),allowed_current_sha256=sorted(allowed),source_inventory=sources,required_supplied_hashes=required,installer_execution_count=0,network_calls=0),indent=2))
print('Package prepared;',len(allowed),'accepted current hashes; 2 installer ASTs parsed, zero executions.')
