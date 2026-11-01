#!/usr/bin/env python3
"""Decodes the ps2_netemu durable debug log image.
Parses Sector 0 (NETEMULG Header) and Sectors 1..127 (LOGR Records).
Compatible with Python 3.8+.
"""
import sys
import struct
from pathlib import Path

def is_printable_ascii(b: bytes) -> bool:
    return all(32 <= x <= 126 for x in b)

def tag_to_str(tag_val: int) -> str:
    b = struct.pack('>I', tag_val)
    if is_printable_ascii(b):
        return f"'{b.decode('ascii')}'"
    return f"0x{tag_val:08X}"

def decode_log(data: bytes, verbose: bool = True):
    if len(data) < 512:
        raise ValueError(f"File too small ({len(data)} bytes < 512)")

    result = {
        'header': None,
        'records': [],
        'is_blank': True
    }

    if any(b != 0 for b in data):
        result['is_blank'] = False
    else:
        if verbose:
            print("File is 100% all-zeros (unwritten placeholder).")
        return result

    # Sector 0: Header
    sec0 = data[:512]
    magic = sec0[:8]
    if magic == b'NETEMULG':
        version, hdr_sz, file_sz, sec_sz, max_rec, next_idx, boot_tb, clean, rec_count = struct.unpack_from('>IIIIIIQII', sec0, 8)
        result['header'] = {
            'magic': 'NETEMULG',
            'version': version,
            'header_size': hdr_sz,
            'file_size': file_sz,
            'sector_size': sec_sz,
            'max_records': max_rec,
            'next_record_idx': next_idx,
            'boot_tb': boot_tb,
            'clean_shutdown': clean,
            'record_count': rec_count
        }
        if verbose:
            print("=== LOG HEADER (Sector 0) ===")
            print(f"Header Magic:     'NETEMULG'")
            print(f"Version:          0x{version:08X}")
            print(f"Header Size:      {hdr_sz} bytes")
            print(f"File Size:        {file_sz} bytes")
            print(f"Sector Size:      {sec_sz} bytes")
            print(f"Capacity:         {max_rec} records")
            print(f"Next Record Idx:  #{next_idx}")
            print(f"Boot TB:          0x{boot_tb:016X} ({boot_tb} ticks)")
            status_str = "CLEAN" if clean == 1 else "UNCOMMITTED / CRASH"
            print(f"Shutdown:         {status_str}")
            print(f"Record Count:     {rec_count}")
    else:
        if verbose:
            print(f"Header magic mismatch: {magic!r}")

    # Sectors 1..127
    total_sectors = len(data) // 512
    if verbose:
        print("\n=== LOG RECORDS ===")

    records = []
    header_boot_tb = result['header']['boot_tb'] if result['header'] else 0

    for s in range(1, total_sectors):
        off = s * 512
        sec = data[off : off + 512]
        if all(b == 0 for b in sec):
            continue

        rec_magic = sec[:4]
        if rec_magic == b'LOGR':
            seq, tag, flags, tb, a, b, boot_id = struct.unpack_from('>IIIQQQQ', sec, 4)
            # Text starts at offset 72 (0x48), max 440 bytes
            raw_text = sec[72:512]
            null_pos = raw_text.find(b'\x00')
            if null_pos != -1:
                raw_text = raw_text[:null_pos]
            text = raw_text.decode('latin-1', errors='replace')

            is_current = (boot_id == header_boot_tb) if header_boot_tb != 0 else True

            rec_dict = {
                'sector': s,
                'seq': seq,
                'tag': tag,
                'tag_str': tag_to_str(tag),
                'flags': flags,
                'tb': tb,
                'a': a,
                'b': b,
                'boot_id': boot_id,
                'is_current': is_current,
                'text': text,
                'crash_point': False
            }
            records.append(rec_dict)
        else:
            records.append({
                'sector': s,
                'raw_magic': rec_magic,
                'raw_hex': sec[:32].hex()
            })

    # Analyze WAL sequences for [CRASH POINT] detection
    # In WAL, each PRE record should be followed by a POST (or TIMEOUT/END)
    TAG_PRE  = 0x50524520  # 'PRE '
    TAG_POST = 0x504F5354  # 'POST'
    TAG_TMO  = 0x544D4F20  # 'TMO '
    TAG_END  = 0x454E4420  # 'END '

    current_records = [r for r in records if r.get('is_current', True) and 'tag' in r]
    pending_pre = None

    for r in current_records:
        tag = r['tag']
        if tag == TAG_PRE:
            if pending_pre is not None:
                # Previous PRE was never resolved!
                pending_pre['crash_point'] = True
            pending_pre = r
        elif tag == TAG_POST:
            if pending_pre is not None:
                pending_pre = None
        elif tag in (TAG_TMO, TAG_END):
            pending_pre = None

    if pending_pre is not None:
        pending_pre['crash_point'] = True

    result['records'] = records

    crash_found = None
    if verbose:
        for r in records:
            s = r['sector']
            if 'tag' in r:
                tag_display = r['tag_str']
                seq = r['seq']
                tb = r['tb']
                a = r['a']
                b = r['b']
                boot_id = r['boot_id']
                text = r['text']
                status_notes = []
                if not r['is_current']:
                    status_notes.append(f"[STALE boot_id=0x{boot_id:016X}]")
                if r['crash_point']:
                    status_notes.append("[CRASH POINT]")
                    crash_found = r

                note_str = (" " + " ".join(status_notes)) if status_notes else ""
                print(f"[Sector {s:03d}] Seq={seq:04d} Tag={tag_display} BootID=0x{boot_id:016X} TB=0x{tb:016X} A=0x{a:016X} B=0x{b:016X} -> {text}{note_str}")
            else:
                print(f"[Sector {s:03d}] Raw (magic {r['raw_magic']!r}): {r['raw_hex']}...")

        print(f"\nTotal populated log records found: {len(records)}")
        if crash_found:
            print(f"\n*** [CRASH POINT DETECTED] ***")
            print(f"Execution did not return from call logged at Sector {crash_found['sector']} (Seq={crash_found['seq']}):")
            print(f"  Command / Step : {crash_found['text']}")
            print(f"  Timestamp (TB) : 0x{crash_found['tb']:016X}")
            print(f"  Parameters     : A=0x{crash_found['a']:016X}, B=0x{crash_found['b']:016X}")
        elif any(r.get('tag') == TAG_END for r in current_records):
            print("\n*** Log execution completed normally (TAG_END found) ***")

    return result

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_netemu_log.bin>")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)

    data = p.read_bytes()
    decode_log(data, verbose=True)

if __name__ == '__main__':
    main()
