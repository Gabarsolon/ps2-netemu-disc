#include "owned.h"

static void fence(void) { __atomic_thread_fence(__ATOMIC_SEQ_CST); }
static int empty(void) {
    for (u32 i=0;i<12;++i) if (MQ[i]) return 0;
    return 1;
}
/* Publication checksum, not an authentication/SMP primitive. Includes both
 * halves of every immutable mailbox field; checked before any heap read. */
static u64 seal(void) {
    u64 x=M->a ^ M->p ^ M->e ^ M->boot ^ M->diag ^ M->saved ^ M->inside ^ (M->control>>32);
    x^=x>>33; x*=0xff51afd7ed558ccdULL; x^=x>>33;
    return MAGIC | (u32)(x^(x>>32));
}
static int pool(u64 p,u64 e) {
    return p && !(p&0xfffff) && p<=~0ULL-0x100000 &&
        (e&~0x0f800000ULL)==0x80000000ULL && !(e&0x7fffff) &&
        Q(0x934960)==0x60000 && Q(0x934968)==1 &&
        Q(0x934970)==p && Q(0x934980)==e && Q(0x24565b8)==e &&
        Q(H)==0x40000 && Q(H+0x28)==e+0x20000 && Q(H+0x10040)==e+0x20000;
}
/* Fixed-address inspection. Never follow any pointer read from this bank. */
static __attribute__((noinline)) int admit(u64 p,u64 e,u64 *count,u64 *fresh,u64 limit) {
    if (!pool(p,e) || Q(H+8)!=T || Q(T)) return 0;
    u64 b=Q(H+0x18), off=0;
    *count=b;
    if (b<1 || b>limit) return 0;
    for (u32 i=0;i<4096;++i) {
        u64 a=H+0x40+16ULL*i;
        u64 next=Q(a), attr=Q(a+8), size=(attr>>32)&0x7fff;
        if (next!=(i==4095?0:a+16) || (attr&0x00008000ffffffffULL)) return 0;
        if (i<b) {
            if (!size || ((attr>>48)&0x7fff)!=off || size>4096-off) return 0;
            if (!*fresh && !(attr>>63) && size>=128) *fresh=e+0x20000+off*64;
            off+=size;
        } else if (attr) return 0;
    }
    return off==4096;
}
static int range(u64 a,u64 n,u64 e) {
    return !(a&63) && a>=e+0x20000 && a-(e+0x20000)<0x40000 &&
        n && n<=0x40000-(a-(e+0x20000));
}
static u64 command(u64 a) { return (a+0x107f)&~127ULL; }
static int layout(u64 a,u64 p,u64 e) {
    if (!range(a,N,e)) return 0;
    u64 c=command(a), d=c+128;
    return c>=a+0x1000 && c-a<=N-64 && d-a<=N-2048 &&
        !(c&127) && !(d&127) &&
        c>=e && d>=e && c-e<=0x100000-64 && d-e<=0x100000-2048 &&
        !((p+(c-e))&127) && !((p+(d-e))&127);
}
static u64 pattern(u32 i,u64 salt) { return salt ^ (0x0101010101010101ULL*i); }
/* These are the only dynamic persistent store sites. Called solely following
 * successful fresh native allocation + range/layout/pool guards under EE0. */
static __attribute__((noinline)) void initialize(u64 a,u64 p,u64 e,u64 boot,
        u64 result,u64 diag,u64 saved,u64 inside,u64 pir,u64 b) {
    volatile u64 *l=(volatile u64 *)a;
    u64 c=command(a), d=c+128, cs=0, ds=0;
    for (u32 i=0;i<0x1000/8;++i) l[i]=0;
    for (u32 i=0;i<8;++i) {
        u64 v=pattern(i,0x434d445041543031ULL);
        ((volatile u64 *)c)[i]=v; cs+=v;
    }
    for (u32 i=0;i<256;++i) {
        u64 v=pattern(i,0x4441544150415431ULL);
        ((volatile u64 *)d)[i]=v; ds+=v;
    }
    l[L_COOKIE]=a^p^e^boot^SALT; l[L_A]=a; l[L_N]=N; l[L_P]=p; l[L_E]=e;
    l[L_ALPAR]=p+(a-e); l[L_C]=c; l[L_CLPAR]=p+(c-e);
    l[L_DATA]=d; l[L_DLPAR]=p+(d-e); l[L_BOOT]=boot; l[L_RESULT]=result;
    l[L_DIAG]=diag; l[L_SAVED]=saved; l[L_INSIDE]=inside; l[L_PIR]=pir;
    l[L_FLAGS]=0; l[L_COUNT]=b; l[L_HEADROOM]=4092-b;
    l[L_CMDSUM]=cs; l[L_DATASUM]=ds;
    fence(); l[L_MAGIC]=LEASE; fence();
}

/* PROBE 7j: build an lv1_atapi_cmnd_block (0x40 bytes) in an owned-block scratch
 * slot (arg0, same bounded pattern as initialize/probe_store). Layout matches LV1
 * / ps2_emu fn_00022138: pkt[0x20] (CDB), pktlen@0x20, blocks@0x24, block_size@0x28,
 * proto@0x2c, in_out@0x30, buffer@0x38. CDB = SCSI READ(10): 0x28, LBA(4 BE) at
 * bytes 2..5, transfer length (2 BE)=1 at bytes 7..8. proto=3 (DMA), in_out=1 (read),
 * block_size=2048, buffer = the DMA bus address. */
static __attribute__((noinline,unused)) void build_atapi(u64 a,u64 lba,u64 dma) {
    volatile u64 *s=(volatile u64 *)a;
    s[0]=0x2800000000000000ULL|((lba&0xffffffffULL)<<16); /* 28 00 LBA[2..5] 00 TLhi */
    s[1]=0x0100000000000000ULL;                            /* TLlo=01, rest 0 */
    s[2]=0; s[3]=0;
    s[4]=0x0000000C00000001ULL;  /* pktlen=12, blocks=1 */
    s[5]=0x0000080000000003ULL;  /* block_size=2048, proto=3 (DMA) */
    s[6]=0x0000000100000000ULL;  /* in_out=1 (read), pad=0 */
    s[7]=dma;                    /* buffer = DMA bus address */
    fence();
}

/* Firmware-route probe store. Block base arrives as an arg (same bounded pattern
 * as initialize): stores land only in free owned-block slots past the lease. */
static __attribute__((noinline)) void probe_store(u64 a,u64 oret,u64 cret) {
    volatile u64 *l=(volatile u64 *)a;
    l[L_OPEN]=oret; l[L_CLOSE]=cret; l[L_PMARK]=PROBE_MARK; fence();
}

u64 owned_startup(u64 a,u64 b,u64 c,u64 d,u64 e0,u64 f,u64 g,u64 h,u64 caller) {
    u64 result=native_startup(a,b,c,d,e0,f,g,h);
    /* Exact patched callsite is the epoch boundary, not a generic warm API. */
    if (!empty()) return result;
    u64 pir=read_pir(), msr=read_msr(), status=CONTEXT, saved=msr, inside=msr;
    u64 flags=(W(0x930f80)!=0)|((u64)(W(0x930f84)!=0)<<1);
    u64 p=0,e=0,alloc=0,attempts=0,count=0;
    u64 boot=__builtin_readcyclecounter();
    if (!boot) return result;
    if (caller==0x18cb8 && (s32)(u32)pir<0 && !(msr&0x4000) &&
        !flags && W(0x930f80)==0 && W(0x930f84)==0) {
        saved=irq_save();
        inside=read_msr();
        /* Saved PR and live EE/PR, stable PIR and acknowledged flags. */
        if (!(saved&0x4000) && !(inside&0xc000) && read_pir()==pir &&
            W(0x930f80)==0 && W(0x930f84)==0 && empty()) {
            p=Q(0x934970); e=Q(0x934980); status=HEAP;
            u64 expected=0;
            if (admit(p,e,&count,&expected,4091)) {
                attempts=1;
                u64 candidate=native_alloc(N,3,0);
                alloc=candidate; /* opaque diagnostic unless status becomes OWNED */
                status=candidate?BAD_RETURN:ZERO;
                if (candidate && candidate==expected && layout(candidate,p,e)) {
                    status=CHANGED;
                    if (pool(p,e) && Q(H+8)==T && !Q(T) &&
                        Q(H+0x18)>=count && Q(H+0x18)<=count+1 &&
                        read_pir()==pir && !(read_msr()&0xc000) &&
                        W(0x930f80)==0 && W(0x930f84)==0 && empty()) {
                        u64 diag=(attempts<<56)|(count<<32)|(u32)pir;
                        initialize(candidate,p,e,boot,result,diag,saved,inside,pir,count);
                        alloc=candidate; status=OWNED;
                    }
                }
            }
        }
        /* Exactly one outer restore, including every normal decline. */
        (void)irq_restore(saved);
        /* FIRMWARE-ROUTE PROBE (test build only): with the owned block held and
         * IRQs restored, make one LV1 open_device call via netemu's FORWARDED
         * guest-sc bridge and record the return. No DMA, no read, no device
         * command here. */
        if (status==OWNED && alloc) {
            /* PROBE 7a: REPOSITORY ENUMERATION (safe, no hardware, no open). Probes
             * 5/6 proved the optical opens and its interrupts route to a guest event
             * port. Before issuing any read we must know the optical's repository
             * dev_id and whether it is a storage node at all. Call netemu's own
             * enumerator (fn_001e9ba0, r2=TOC via trampoline) for the OPTICAL type
             * (bus type 5, dev type 5 -- same as ps2_emu fn_00022460) and, as a
             * control, the FLASH type (5,14) which netemu itself enumerates. The
             * enumerator only reads the LV1 repository (forwarded sc0 internally), so
             * this cannot touch the drive or power off. Store, per device:
             * (found<<32)|(u32)out1_handle. If optical found==1 -> it is a storage
             * repository node -> probe 7b does storage_read(245) (forwarded, no A).
             * If optical found==0 but flash found==1 -> optical is NOT a storage node
             * -> the read needs send_device_command(248)+ATAPI CDB (direct sc1, A). */
            /* PROBE 7d: READ ONE SECTOR from the optical. open -> alloc DMA region
             * (174) -> map it (176) to the owned block's ZEROED scratch gap (alloc+
             * 0x200, between the header and the integrity-checked command/data
             * patterns, so the DMA does not corrupt them) -> storage_read(245) LBA 16
             * (ISO9660/PS2 volume descriptor) -> poll get_async_status(249) until
             * result&0xffffff==0 -> read the DMA'd first 8 bytes back via Q(). All
             * forwarded sc0, no A. w0 = the sector's first 8 bytes (expect 0x0143443030
             * 310100 = 01 "CD001" 01 on a valid PS2 disc). w1 = (map_ret<<48)|result.
             * lpar_scratch = p+(alloc-e)+0x200 must sit in netemu's DMA window
             * (< 0x3ffffff; the owned block does). Fail-open at each nonzero step. */
            /* PROBE 7f: map(176) returned -17 (LV1_ILLEGAL_PARAMETER_VALUE) in 7d/7e
             * because the DMA target was not PAGE-ALIGNED. The 8KB owned block cannot
             * host a page-aligned buffer clear of its integrity patterns, and the
             * allocator caps allocations (native_alloc(0x3000) returns 0). So DMA into
             * FREE POOL RAM past the owned block: ea2 = (alloc+0x4000)&~0xfff is
             * page-aligned, inside the 0x40000 LPAR pool, in netemu's DMA window
             * (< 0x3ffffff), and not handed out by the allocator -- so the owned block
             * and its snapshot machinery stay fully intact. alloc+map 0x1000 (sizes
             * matched) -> storage_read LBA 16 -> poll -> read back via Q(ea2). w0 =
             * sector first 8 bytes (expect 0x0143443030310100 = 01 "CD001" 01). */
            /* PROBE 7o (CONTROL): all optical send_device_command(248) attempts returned
             * -6 (NO_ENTRY) through 7n, with the ABI verified, patch A applied and the
             * full IRQ setup (18/197/28). Before concluding the optical is fundamentally
             * not a commandable storage device for the PS2_NE LPAR, test our core storage
             * machinery against the KNOWN-GOOD device: FLASH (bus type 5, dev type 14),
             * which netemu itself reads via storage_read (dev_id 4, proven in 7b). Same
             * enum -> open -> alloc(174) -> map(176) -> storage_read(245) region 2 LBA 0 ->
             * poll -> read back. flash status==0 + nonzero data8 => our machinery is good
             * and the optical -6 is device-specific (ownership/registration). flash ALSO
             * -6 => the problem is our owned_startup context/timing, not the optical. */
            /* PROBE 7p (ROOT-CAUSE FIX for -6 NO_ENTRY in 7j-7n): lv1.elf RE
             * proved func_0x0025397c checks data_buf (arg5 / cdb[0x38]) against
             * the LPAR memory-region RB-tree via func_0x002ce74c and returns -6
             * when given the IOMMU bus address dma (0xc0000000) instead of lpar2.
             * Switch back to optical (5,5,0), pass lpar2 in both CDB+0x38 and
             * arg5 of send_device_command(248), poll check_async_status(254)
             * with the returned tag up to 200k iterations (~250ms), invalidate
             * ea2 with dcache_flush, and record data8 + packed (sstat,rc,async). */
            u64 o1=0,o2=0;
            u64 of=(u64)(native_repo_enum(5,5,0,&o1,&o2)&0xff);    /* OPTICAL */
            u64 bus=of?native_repo_busid(o1):0;
            u64 dev=of?native_repo_devid(o1,o2):0;
            u64 data8=0, w1=PROBE_NOCLOSE;
            if (of && lv1_open_device(bus,dev,0)==0) {
                u64 port=lv1_event_rx_port();                  /* 18 -> port */
                u64 cret=lv1_connect_irq_event(bus,dev,port,0); /* 197 -> status */
                u64 pret=lv1_connect_irq_plug(9,port);         /* 28 -> status (virq 9) */
                (void)port; (void)cret; (void)pret;
                u64 dma=lv1_alloc_dma(bus,dev,0x1000,0xC,0);   /* 4KB io_pagesize (0xC) */
                if (dma) {
                    u64 ea2=(alloc+0x4000)&~0xfffULL;        /* page-aligned free pool RAM */
                    u64 lpar2=p+(ea2-e);
                    u64 mret=lv1_map_dma(bus,dev,lpar2,dma,0x1000,0xe000000000000800ULL);
                    if (mret==0) {
                        u64 cb=alloc+0x100;
                        u64 cb_lpar=p+(cb-e);
                        build_atapi(cb,16,lpar2);
                        u64 scmd=lv1_send_device_command(dev,1,cb_lpar,0x40,lpar2,2048);
                        u64 sstat=(scmd>>32)&0xffffffffULL;
                        u64 tag=scmd&0xffffffffULL;
                        u64 res=0xffffffff00000000ULL;
                        if (sstat==0) {
                            for (u32 i=0;i<200000;++i) {
                                res=lv1_check_async_status(dev,tag);
                                if ((res>>32)==0) break;
                            }
                        }
                        dcache_flush(ea2,0x1000/128);
                        data8=Q(ea2);
                        w1=((sstat&0xffffULL)<<48)|(((res>>32)&0xffffffULL)<<24)|(res&0xffffffULL);
                    } else w1=(mret<<48)|0xBAD;
                }
                (void)lv1_close_device(bus,dev);
            }
            probe_store(alloc,data8,w1);
        }
    }
    if (!empty()) return result;
    M->control=(status<<32)|READY; M->a=alloc; M->p=p; M->e=e;
    M->boot=boot; M->start=0; M->last=0; M->count=0;
    M->diag=(attempts<<56)|(flags<<48)|((count>4096?4096:count)<<32)|(u32)pir;
    M->saved=saved; M->inside=inside;
    fence(); M->magic=seal(); fence();
    return result;
}

/* Pointer validation precedes ANY lease dereference. A mailbox alone cannot
 * mint ownership: lease/cookie/tuple must match the fully published startup. */
static __attribute__((noinline)) u64 valid(void) {
    if ((M->magic&0xffffffff00000000ULL)!=MAGIC || !M->boot || M->magic!=seal()) return 0;
    u64 ctl=M->control, status=ctl>>32, phase=(u32)ctl;
    if (status<OWNED || status>CHANGED || phase<READY || phase>PUBLISHING) return 0;
    if (M->diag & 0x00fc000000000000ULL) return 0;
    u64 tries=M->diag>>56, b=(M->diag>>32)&0xffff;
    if (tries>1 || b>4096) return 0;
    if (status!=OWNED) {
        if (status<=ZERO && M->a) return 0;
        if ((status==CONTEXT && tries) || (status==HEAP && tries) ||
            (status>=ZERO && tries!=1)) return 0;
        return 1;
    }
    u64 a=M->a,p=M->p,e=M->e,boot=M->boot;
    if (tries!=1 || b<1 || b>4091 || (M->diag&0x0003000000000000ULL) || (s32)(u32)M->diag>=0 ||
        (M->saved&0x4000) || (M->inside&0xc000) || !pool(p,e) || !layout(a,p,e)) return 0;
    const volatile u64 *l=(const volatile u64 *)a;
    u64 c=command(a), data=c+128;
    return l[L_MAGIC]==LEASE && l[L_COOKIE]==(a^p^e^boot^SALT) &&
        l[L_A]==a && l[L_N]==N && l[L_P]==p && l[L_E]==e &&
        l[L_ALPAR]==p+(a-e) && l[L_C]==c && l[L_CLPAR]==p+(c-e) &&
        l[L_DATA]==data && l[L_DLPAR]==p+(data-e) && l[L_BOOT]==boot &&
        l[L_DIAG]==M->diag && l[L_SAVED]==M->saved && l[L_INSIDE]==M->inside &&
        (u32)l[L_PIR]==(u32)M->diag && l[L_FLAGS]==0 &&
        l[L_COUNT]==b && l[L_HEADROOM]==4092-b ? a:0;
}
static __attribute__((noinline)) int patterns(u64 a) {
    /* valid() is mandatory at each callsite; addresses recomputed, not loaded. */
    u64 c=command(a),d=c+128,cs=0,ds=0;
    for (u32 i=0;i<8;++i) { u64 v=Q(c+8ULL*i); if(v!=pattern(i,0x434d445041543031ULL)) return 0; cs+=v; }
    for (u32 i=0;i<256;++i) { u64 v=Q(d+8ULL*i); if(v!=pattern(i,0x4441544150415431ULL)) return 0; ds+=v; }
    return Q(a+8*L_CMDSUM)==cs && Q(a+8*L_DATASUM)==ds;
}
static int ui(u8 reason) {
    return Y(0x934161)==reason && Q(0x306fc68)==0x30700d0 && Q(0x30700d0)==0x949cb8;
}
static int hdd(void) {
    return Y(0x241c8d5)==1 && Y(0x241c8c8)==0 && Q(0x241c860)==3 &&
        Q(0x241c888)==0 && Q(0x241c890)==0 && Q(0x241c898)==0 && W(0x3055180)==0;
}
static void phase(u32 p) { M->control=(M->control&0xffffffff00000000ULL)|p; fence(); }
static void tick(void) {
    u64 lease=valid();
    if (!lease) return;
    u32 p=(u32)M->control;
    if (p==READY) {
        if (!ui(0) || !hdd()) return;
        u64 now=native_clock();
        if (!now || valid()!=lease || !ui(0) || !hdd()) return;
        if (M->start || M->last || M->count || now<M->boot) return;
        M->start=now; M->last=now; M->count=0; fence(); phase(TIMER); return;
    }
    if (p!=TIMER) return;
    if (!ui(0)) { phase(ABORTED); return; }
    u64 now=native_clock();
    if (valid()!=lease) return;
    if (!now || !ui(0)) { phase(ABORTED); return; }
    u64 start=M->start,last=M->last,count=M->count;
    if (!start || start<M->boot || last<start || now<last || count>100) { phase(ABORTED); return; }
    if (count<100) ++count;
    M->last=now; M->count=count;
    if (now-start<DELAY || count<100) return;
    if (valid()!=lease || !ui(0)) { phase(ABORTED); return; }
    if (!hdd()) return;
    if (lease>1 && !patterns(lease)) { phase(ABORTED); return; }
    phase(PUBLISHING);
    if (valid()!=lease || !ui(0)) { phase(ABORTED); return; }
    if (!hdd()) { phase(TIMER); return; }
    phase(TERMINAL);
    if (valid()!=lease || !ui(0)) { phase(ABORTED); return; }
    if (!hdd()) { phase(TIMER); return; }
    *(volatile u8 *)0x934161ULL=2; fence();
}
u64 owned_refresh(u64 a,u64 b,u64 c,u64 d,u64 e,u64 f,u64 g,u64 h) {
    u64 result=native_refresh(a,b,c,d,e,f,g,h); tick(); return result;
}
static __attribute__((noinline)) void snapshot(u64 result) {
    u64 lease=valid();
    if (!lease || (u32)M->control!=TERMINAL || !ui(2) || !hdd()) return;
    u64 now=__builtin_readcyclecounter(), last=M->last;
    if (!M->start || M->start<M->boot || last<M->start ||
        last-M->start<DELAY || M->count!=100 || now<last ||
        now-last>120ULL*(1ULL<<26)) return;
    if (lease>1 && !patterns(lease)) return;
    u64 marker=M->control;
    if (valid()!=lease || M->control!=marker || !ui(2) || !hdd()) return;
    phase(CONSUMED);
    volatile u64 sec[64]; volatile u64 statbuf[6];
    for (u32 i=0;i<64;++i) sec[i]=0;
    for (u32 i=0;i<6;++i) statbuf[i]=0;
    sec[0]=0x4f574e5345433100ULL; /* OWNSEC1 + NUL */
    sec[1]=0x0001000000000200ULL; sec[2]=marker; sec[3]=now;
    sec[4]=0xb46100; sec[5]=2; sec[6]=result;
    sec[7]=M->a; /* exact allocator return; never a lease on a decline */
    for (u32 i=0;i<12;++i) sec[8+i]=MQ[i];
    if (lease>1) {
        const volatile u64 *l=(const volatile u64 *)lease;
        for (u32 i=0;i<L_END;++i) sec[20+i]=l[i];
        sec[62]=l[L_OPEN]; sec[63]=l[L_CLOSE]; /* firmware-route probe results */
        sec[42]=1; sec[43]=Q(command(lease)); sec[44]=Q(command(lease)+56);
        sec[45]=Q(command(lease)+128); sec[46]=Q(command(lease)+128+2040);
    }
    sec[47]=Q(0x306fc68); sec[48]=Q(0x30700d0);
    sec[49]=Q(0x241c860); sec[50]=Q(0x241c888); sec[51]=Q(0x241c890); sec[52]=Q(0x241c898);
    sec[53]=((u64)W(0x241c850)<<32)|W(0x241c8a8);
    sec[54]=((u64)W(0x3055180)<<32)|((u64)Y(0x241c8c8)<<24)|((u64)Y(0x241c8d5)<<16)|((u64)Y(0x934161)<<8);
    if (valid()!=lease || M->control!=((marker&0xffffffff00000000ULL)|CONSUMED) || !ui(2) || !hdd()) return;
    s32 fd=stock_ufs_open(0,"/tmp/netemu_owned_snapshot.bin");
    if (fd<0 || fd>7) return;
    if (!stock_ufs_stat(fd,(void *)statbuf) && statbuf[5]==65536) {
        sec[55]=(u32)fd;
        for (u32 i=0;i<6;++i) sec[56+i]=statbuf[i];
        (void)stock_raw_write(fd,0,(const void *)sec,512);
    }
    (void)stock_ufs_close(fd);
}
u64 owned_shutdown(u64 a,u64 b,u64 c,u64 d,u64 e,u64 f,u64 g,u64 h) {
    u64 result=native_shutdown(a,b,c,d,e,f,g,h);
    if (a==0xb46100 && b==2 && Y(0x934161)==2) snapshot(result);
    return result;
}
