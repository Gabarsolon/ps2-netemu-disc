"""Offline decoder; rejects other formats, reports unknowns explicitly."""
import argparse
import json
from pathlib import Path
import struct

NAMES={0:'invalid target tuple; UNKNOWN',1:'unsupported HTAB size; UNKNOWN',
       2:'HTAB changed or coverage rejected; UNKNOWN',3:'call95 failed; UNKNOWN',
       4:'no exact V match; UNKNOWN',5:'ambiguous V matches; UNKNOWN',6:'unique exact V match'}
CAPTURE_NAMES=['marker','UI object','UI vtable','HDD device','HDD completed',
               'HDD status','HDD expected','CDVD EA','CDVD size','CDVD LPAR',
               'HDD flags/count','packed lock/HDD/UI status']
META_NAMES={20:'shutdown CDVD EA',21:'shutdown CDVD size',22:'shutdown CDVD LPAR',
            23:'HTAB handle',24:'HTAB bytes',25:'pool useful extent',26:'pool native flags',
            27:'pool LPAR P',28:'pool CPU EA E',29:'published E',30:'payload base',
            31:'heap H+28 (same fixed word as payload base)',32:'initialized sentinel',
            33:'first bank head H+8',34:'first bank next H+38',
            35:'first bank growth-marker attribute H+10008',36:'native stat file size',37:'fd'}

def decode(b):
    if len(b) not in (512,65536): raise ValueError('expected 512-byte sector or exact 65536-byte private file')
    q=struct.unpack('>64Q',b[:512])
    if q[0]!=0x4d41505345433100 or q[1]!=0x0001000000000200:
        raise ValueError('not MAPSEC1 version 1 / 512 bytes')
    if any(q[i] for i in [7,38,39,*range(56,64)]): raise ValueError('reserved words nonzero')
    maps=[]
    for name,base in [('captured CDVD',40),('first native heap pool',48)]:
        ea,virt,v,groups,outcome,rc,counts,found=q[base:base+8]
        if outcome not in NAMES: raise ValueError('unknown outcome code')
        calls,matches=counts>>32,counts&0xffffffff
        if calls>4 or matches>16: raise ValueError('invalid scan counts')
        r=dict(target=name,EA=hex(ea),virtual=hex(virt),expected_primary_V=hex(v),
               expected_secondary_V=hex(v|2) if v else None,
               primary_group=groups>>32,secondary_group=groups&0xffffffff,
               outcome=NAMES[outcome],last_call_status=hex(rc),queries=calls,matches=matches,
               WIMG=None,attribute_interpretation='UNKNOWN')
        if outcome==6:
            if calls!=4 or matches!=1 or rc!=0: raise ValueError('unique requires a successful full scan')
            low=(found>>16)&65535; wimg=found&65535
            if wimg!=low&0x78: raise ValueError('inconsistent WIMG mask')
            index=found>>32; primary,secondary=groups>>32,groups&0xffffffff
            if not (primary<=index<primary+8 or secondary<=index<secondary+8): raise ValueError('match index outside groups')
            r.update(matched_index=index,low_R16=hex(low),WIMG=hex(wimg),
                     attribute_interpretation={0x10:'M',0x20:'I',0x28:'I|G'}.get(wimg,'other WIMG bits; raw value only'))
        elif found!=0xffffffff00000000: raise ValueError('unknown result must suppress index/R16/WIMG')
        maps.append(r)
    return dict(format='MAPSEC1',version=1,sector_bytes=512,marker=hex(q[2]),timebase=hex(q[3]),
                native_object=hex(q[4]),reason=q[5],original_native_result=hex(q[6]),
                capture={k:hex(v) for k,v in zip(CAPTURE_NAMES,q[8:20])},
                metadata={name:hex(q[i]) for i,name in META_NAMES.items()},mappings=maps,
                trailing_bytes_zero=not any(b[512:]),
                limits='Samples are not atomic or ownership. HPTE low-R omits upper RPN and does not establish active CPU SLB/TLB, full physical/LPAR identity, cache visibility, optical delivery or durability. WIMG names are architectural interpretation.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file',type=Path)
    args=p.parse_args(); print(json.dumps(decode(args.file.read_bytes()),indent=2))
