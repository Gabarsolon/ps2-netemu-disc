"""Offline OWNSEC1 v1 decoder. Test bytes are patterns, never disc data."""
from pathlib import Path
import argparse, hashlib, json, struct
MASK=(1<<64)-1
MAGIC=0x4f574e3100000000
LEASE=0x4f574e4c45415331
SALT=0xb56d847ace390f21
STATUSES={1:'owned',2:'context declined',3:'heap admission declined',4:'allocator zero',5:'allocator return rejected',6:'post-allocation metadata/context changed'}
LEASE_FIELDS=['magic','cookie','A','N','P','E','allocation LPAR','command EA','command LPAR',
              'data EA','data LPAR','boot TB','startup native result','diagnostic','saved MSR','inside MSR',
              'SPR088','handshake flags (both zero)','admission B','headroom to B4092','command checksum','data checksum']
def decode(data):
    if len(data) not in (512,65536):raise ValueError('Expected 512-byte sector or 65536-byte precreated file')
    q=struct.unpack('>64Q',data[:512])
    def need(condition,message):
        if not condition:raise ValueError(message)
    need(q[0]==0x4f574e5345433100 and q[1]==0x1000000000200,'Wrong OWNSEC1 version/size')
    need(q[4:6]==(0xb46100,2),'Wrong shutdown context')
    m=q[8:20]; status=q[2]>>32
    need(status in STATUSES and q[2]&0xffffffff==3,'Wrong terminal marker/status')
    need(m[1]==(status<<32)|4,'Mailbox not consumed')
    x=m[2]^m[3]^m[4]^m[5]^m[9]^m[10]^m[11]^status
    x^=x>>33;x=x*0xff51afd7ed558ccd&MASK;x^=x>>33
    need(m[0]==MAGIC|((x^(x>>32))&0xffffffff),'Publication checksum mismatch')
    attempts=m[9]>>56; count=(m[9]>>32)&0xffff; flags=(m[9]>>48)&3
    need(q[7]==m[2],'Allocator return mismatch')
    need(not(m[9]&0x00fc000000000000) and attempts<=1 and count<=4096,'Malformed diagnostics')
    need(0<m[5]<=m[6]<=m[7]<=q[3] and m[7]-m[6]>=20*79800000 and m[8]==100,'Invalid boot/timer facts')
    need(q[3]-m[7]<=120*(1<<26),'Stale snapshot')
    need(q[47:53]==(0x30700d0,0x949cb8,3,0,0,0) and q[54]==0x10200,'UI/HDD/reason mismatch')
    need(0<=q[55]<=7 and q[61]==65536 and q[62:]==(0,0),'Invalid fd/stat/reserved fields')
    lease={}
    if status==1:
        l=q[20:42];a,p,e,boot=m[2:6];c=(a+0x107f)&~127;d=c+128
        need(p and p%0x100000==0 and p<=MASK-0x100000 and e&~0xf800000==0x80000000,'Pool geometry')
        need(a%64==0 and e+0x20000<=a<=e+0x60000-8192,'Allocation bounds')
        need(attempts==1 and flags==0 and m[9]&0x80000000 and not(m[10]&0x4000) and not(m[11]&0xc000),'Startup context')
        need(c>=a+0x1000 and d+2048<=a+8192 and c%128==d%128==0,'Layout')
        need(l[:12]==(LEASE,a^p^e^boot^SALT,a,8192,p,e,p+a-e,c,p+c-e,d,p+d-e,boot),'Lease tuple mismatch')
        need(l[13:16]==(m[9],m[10],m[11]) and l[16]&0xffffffff==m[9]&0xffffffff and l[17]==0 and 1<=l[18]<=4091 and l[18]==count and l[19]==4092-l[18],'Lease guards')
        def pattern(i,salt):return salt^(0x0101010101010101*i&MASK)
        cs=sum(pattern(i,0x434d445041543031) for i in range(8))&MASK
        ds=sum(pattern(i,0x4441544150415431) for i in range(256))&MASK
        need(l[20:]==(cs,ds) and q[42]==1,'Pattern checksums/verdict')
        need(q[43:47]==(pattern(0,0x434d445041543031),pattern(7,0x434d445041543031),pattern(0,0x4441544150415431),pattern(255,0x4441544150415431)),'Pattern samples')
        lease={k:hex(v) for k,v in zip(LEASE_FIELDS,l)}
    else:
        need((status>4 or m[2]==0) and q[20:47]==(0,)*27,'Declined snapshot contains lease data')
        need(attempts==(0 if status in (2,3) else 1),'Declined attempt count')
    return dict(format='OWNSEC1',version=1,status=STATUSES[status],timebase=hex(q[3]),
        original_shutdown_result=hex(q[6]),mailbox=[hex(v) for v in m],
        attempts=attempts,admission_B=count,primary_h=m[9]>>30&1,initial_handshake_nonzero_flags=flags,
        allocator_return=hex(q[7]),owned_pointer=hex(m[2]) if status==1 else None,
        requested_N=8192 if attempts else 0,
        lease=lease,pattern_pass=q[42]==1,ui_hdd_valid=True,fd=q[55],stat=[hex(v) for v in q[56:62]],
        trailing_bytes_zero=not any(data[512:]),file_sha256=hashlib.sha256(data).hexdigest(),
        limits='Owned test patterns only. No physical read, cache attribute/visibility, DMA, hardware execution, UFS deadline or durable delivery proof.')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
    result=decode(a.input.read_bytes());text=json.dumps(result,indent=2)+'\n'
    if a.output:
        allowed=Path(__file__).resolve().parents[2]/'local_only/owned_control'
        need=a.output.resolve();assert need.is_relative_to(allowed.resolve()),'Generated reports stay under local_only/owned_control'
        a.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
