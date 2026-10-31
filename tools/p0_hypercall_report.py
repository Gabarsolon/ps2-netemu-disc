"""Summarize Ghidra-decoded sites; never disassemble outside Ghidra.

The local constant walk is an inventory aid, not proof of reachability.
"""
from pathlib import Path
import collections, json, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'local_only'/'analysis'
sites=json.loads((OUT/'sc_inventory.json').read_text())
source=(ROOT/'local_only'/'research'/'lv1call_web.txt').read_text(encoding='utf-8')
names={int(num):name for name,num in re.findall(r'LV1_CALL\((\w+),\s*\d+,\s*\d+,\s*(\d+)\s*\)',source)}
direct=[s for s in sites if 'lev=1' in s['scan']]
groups=collections.defaultdict(list)
for s in sites:
    if s['forwarded']:
        groups[(s['hypercall'],s['descriptor_start'])].append(s)
lines=['# P0 LV1 call inventory', '',
       '**PROVEN (local decoding):** Ghidra decoded all 557 opcode matches. There are 20 `sc 1` words, of which one is an opcode-table entry rather than an identified executable callsite. The remaining 537 words are `sc 0`; only the constant high-bit syscall subset below is classified as forwarding to LV1. Opcode matches alone do not prove execution.', '',
       '**INFERRED:** number-to-name mappings use the public Linux header; locally reconstructed r11 values and ELFv1 descriptor bounds identify candidate wrappers. Caller counts are unique direct call instruction references in Ghidra, not runtime counts. Indirect calls and unanalysed references can add callers; a zero is a lower bound. A wrapper may contain multiple call numbers. None of this proves partition permission.', '',
       'Source: [Linux LV1 declarations](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/include/asm/lv1call.h); [wiki call reference](https://www.psdevwiki.com/ps3/HV_Syscall_Reference). Raw disassembly/context and descriptor references remain local.', '',
       '## Direct `sc 1` words', '', '| Site | Number | Containing wrapper / block | Direct callers (lower bound) | Interpretation |', '|---|---|---|---:|---|']
for s in direct:
    n=int(s['site'],16)
    number=s.get('hypercall')
    if n==0x13730:
        desc='Opcode template table: excluded from executable-call totals'
        number=None; wrapper='table at 0x13670..'
    elif n==0xca0:
        desc='Dynamic generic forwarder; r11 supplied by guest syscall'
        wrapper='exception bridge 0x0c00'
    elif number==255:
        desc='panic; high confidence numeric identification'
        wrapper=s['function'] or f'trap block {n-4:#x}'
    elif number==162:
        desc='read_virtual_uart; high confidence numeric identification'
        wrapper='guest syscall dispatcher 0x12670'
    elif number==248:
        desc='storage_send_device_command; command 0x88 = ENCDEC path'
        wrapper='0x135fc'
    else:
        desc='Unresolved'; wrapper=s['function'] or 'no function boundary'
    direct_count=len({r['from'] for r in s['references'] if 'CALL' in r['type']})
    lines.append(f"| {s['site']} | {hex(number) if number is not None else 'dynamic / data'} | {wrapper} | {direct_count} | {desc} |")
lines+=['','## Constant guest calls forwarded to LV1', '',
        '**INFERRED:** `li r11,N; oris r11,r11,0x8000; sc 0` reaches the bridge at `0xc50..0xcbc`; `xoris` removes the high bit before `sc 1` at `0xca0`. The bridge checks the number and a privilege table. Local constants below must not be interpreted as a permission allow-list.', '',
        '| Number (hex / decimal) | Public name / confidence | Wrapper entry | Direct callers (lower bound) | Guest `sc 0` sites |',
        '|---|---|---|---:|---|']
for (num,wrapper),rows in sorted(groups.items()):
    refs=[]
    for s in rows: refs.extend(s['references'])
    callsites={r['from'] for r in refs if 'CALL' in r['type']}
    name=names.get(num,'not named in inspected Linux header')
    confidence='high (number)' if num in names else 'UNKNOWN name'
    lines.append(f"| {num:#x} / {num} | {name}; {confidence} | {wrapper} | {len(callsites)} | {', '.join(s['site'] for s in rows)} |")
lines+=['', '## Coverage limits', '',
        '**UNKNOWN:** indirect callers, execution of every recovered wrapper, and runtime device permissions. The local r11 walk deliberately leaves dynamic/unresolved cases unresolved. A name absent from this table may still be issued through a dynamic bridge.', '',
        '**INFERRED:** there is no identified constant `storage_check_async_status` (254) call, or constant `net_*` / `gelic_*` call in this scan. The identified device command (248) is the dedicated ENCDEC command-0x88 path, not an ATAPI optical implementation. Generic open/close are 170/171, not separate storage-open/storage-close numbers.', '']
(ROOT/'docs'/'P0_HYPERCALLS.md').write_text('\n'.join(lines),encoding='utf-8')
print('direct words',len(direct),'forwarded sites',sum(map(len,groups.values())),'wrapper/number groups',len(groups))
