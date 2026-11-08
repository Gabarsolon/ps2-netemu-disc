import struct
from pathlib import Path

def parse_elf_segments(data):
    # 64-bit Big Endian ELF
    e_phoff = struct.unpack_from('>Q', data, 0x20)[0]
    e_phentsize = struct.unpack_from('>H', data, 0x36)[0]
    e_phnum = struct.unpack_from('>H', data, 0x38)[0]
    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, off)
        if p_type == 1: # PT_LOAD
            segments.append((p_offset, p_filesz, p_vaddr, p_memsz))
    return segments

def va_to_offset(segments, va):
    for p_offset, p_filesz, p_vaddr, p_memsz in segments:
        if p_vaddr <= va < p_vaddr + p_filesz:
            return p_offset + (va - p_vaddr)
    return None

def offset_to_va(segments, off):
    for p_offset, p_filesz, p_vaddr, p_memsz in segments:
        if p_offset <= off < p_offset + p_filesz:
            return p_vaddr + (off - p_offset)
    return None

def analyze_lv1_gpu(elf_path, name):
    data = Path(elf_path).read_bytes()
    segments = parse_elf_segments(data)
    print(f"\n=================== {name}: {elf_path} ===================")
    for seg in segments:
        print(f"Segment: file {hex(seg[0])}..{hex(seg[0]+seg[1])} -> VA {hex(seg[2])}..{hex(seg[2]+seg[3])}")

    # Search for hypercall table records:
    # 16-byte records where record[0] is hypercall number
    p170 = struct.pack('>Q', 170)
    p171 = struct.pack('>Q', 171)
    idx = 0
    table_records = {}
    while True:
        idx = data.find(p170, idx)
        if idx == -1: break
        if idx + 16 < len(data) and data[idx + 16:idx + 24] == p171:
            # Found registration table
            start_idx = idx
            while start_idx >= 16:
                prev_num = struct.unpack_from('>Q', data, start_idx - 16)[0]
                if 0 <= prev_num < 256:
                    start_idx -= 16
                else:
                    break
            end_idx = idx
            while end_idx + 16 < len(data):
                next_num = struct.unpack_from('>Q', data, end_idx + 16)[0]
                if 0 <= next_num < 256:
                    end_idx += 16
                else:
                    break
            start_va = offset_to_va(segments, start_idx)
            end_va = offset_to_va(segments, end_idx)
            print(f"HV registration records found at file {hex(start_idx)}..{hex(end_idx)} (VA {hex(start_va)}..{hex(end_va)})")
            for k in range(start_idx, end_idx + 16, 16):
                num, p_val = struct.unpack_from('>QQ', data, k)
                k_va = offset_to_va(segments, k)
                table_records[num] = (k_va, p_val)
            break
        idx += 1

    # Print GPU hypercalls (210 to 228) and others of interest
    gpu_nums = [210, 211, 212, 213, 214, 216, 217, 218, 221, 225, 227, 228]
    for num in gpu_nums:
        if num in table_records:
            k_va, p_val = table_records[num]
            # p_val is pointer to registration structure
            # let's dereference p_val
            p_val_off = va_to_offset(segments, p_val)
            desc_va = None
            code_va = None
            toc_va = None
            if p_val_off is not None and p_val_off + 24 <= len(data):
                # Typically registration struct has descriptor ptr or handler opd
                # Let's inspect the 32 bytes at p_val
                reg_bytes = [hex(x) for x in struct.unpack_from('>4Q', data, p_val_off)]
                # Often reg_struct has ptr to opd or function descriptor
                # Let's see what is inside
                # On PPC64, an OPD is (func_addr, toc_addr, env_addr)
                # Let's see if one of the pointers is an OPD
                for candidate in struct.unpack_from('>4Q', data, p_val_off):
                    cand_off = va_to_offset(segments, candidate)
                    if cand_off is not None and cand_off + 16 <= len(data):
                        f_addr, t_addr = struct.unpack_from('>QQ', data, cand_off)
                        f_off = va_to_offset(segments, f_addr)
                        if f_off is not None:
                            desc_va = candidate
                            code_va = f_addr
                            toc_va = t_addr
                            break
            print(f"  HV {num:3d} (0x{num:02x}): reg={hex(k_va)} struct={hex(p_val)} desc={hex(desc_va) if desc_va else 'None'} code={hex(code_va) if code_va else 'None'} toc={hex(toc_va) if toc_va else 'None'}")
        else:
            print(f"  HV {num:3d} (0x{num:02x}): NOT REGISTERED")

if __name__ == '__main__':
    analyze_lv1_gpu('local_only/fw355/out/lv1.elf', 'FW 3.55 LV1')
    analyze_lv1_gpu('local_only/fw493/lv1.elf', 'FW 4.93 LV1')
