; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@hddlog_init.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@hddlog_write.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@.str = private unnamed_addr constant [24 x i8] c"boot: ps2_netemu_p11_W1\00", align 1
@.str.1 = private unnamed_addr constant [15 x i8] c"scan: rom_cnt=\00", align 1
@.str.2 = private unnamed_addr constant [6 x i8] c" hdd=\00", align 1
@.str.3 = private unnamed_addr constant [13 x i8] c" bus=4 dev=2\00", align 1
@.str.4 = private unnamed_addr constant [33 x i8] c"grd reject: sanity failed (0 hc)\00", align 1
@.str.5 = private unnamed_addr constant [39 x i8] c"finish: ps2_netemu_p9_U1 failed step=1\00", align 1
@.str.6 = private unnamed_addr constant [30 x i8] c"grd ok: lpar & ea sanity pass\00", align 1
@.str.7 = private unnamed_addr constant [22 x i8] c"pre open: bus=4 dev=2\00", align 1
@.str.8 = private unnamed_addr constant [15 x i8] c"post open: rc=\00", align 1
@.str.9 = private unnamed_addr constant [35 x i8] c"pre dma_alloc: sz=0x100000 pexp=20\00", align 1
@.str.10 = private unnamed_addr constant [20 x i8] c"post dma_alloc: rc=\00", align 1
@.str.11 = private unnamed_addr constant [28 x i8] c"post dma_alloc: rc=0 rgn=0x\00", align 1
@.str.12 = private unnamed_addr constant [17 x i8] c"pre map: lpar=0x\00", align 1
@.str.13 = private unnamed_addr constant [8 x i8] c" rgn=0x\00", align 1
@.str.14 = private unnamed_addr constant [14 x i8] c"post map: rc=\00", align 1
@.str.15 = private unnamed_addr constant [13 x i8] c" bus_addr=0x\00", align 1
@.str.16 = private unnamed_addr constant [21 x i8] c"pre tur: cmd_lpar=0x\00", align 1
@.str.17 = private unnamed_addr constant [43 x i8] c"timeout: tur timed out; halting hypercalls\00", align 1
@.str.18 = private unnamed_addr constant [14 x i8] c"post tur: rc=\00", align 1
@.str.19 = private unnamed_addr constant [10 x i8] c" async=0x\00", align 1
@.str.20 = private unnamed_addr constant [8 x i8] c" polls=\00", align 1
@.str.21 = private unnamed_addr constant [8 x i8] c" ticks=\00", align 1
@.str.22 = private unnamed_addr constant [21 x i8] c"pre inq: cmd_lpar=0x\00", align 1
@.str.23 = private unnamed_addr constant [13 x i8] c" buf_lpar=0x\00", align 1
@.str.24 = private unnamed_addr constant [43 x i8] c"timeout: inq timed out; halting hypercalls\00", align 1
@.str.25 = private unnamed_addr constant [14 x i8] c"post inq: rc=\00", align 1
@.str.26 = private unnamed_addr constant [8 x i8] c" resp='\00", align 1
@.str.27 = private unnamed_addr constant [2 x i8] c"'\00", align 1
@.str.28 = private unnamed_addr constant [21 x i8] c"pre cap: cmd_lpar=0x\00", align 1
@.str.29 = private unnamed_addr constant [43 x i8] c"timeout: cap timed out; halting hypercalls\00", align 1
@.str.30 = private unnamed_addr constant [14 x i8] c"post cap: rc=\00", align 1
@.str.31 = private unnamed_addr constant [8 x i8] c" lba=0x\00", align 1
@.str.32 = private unnamed_addr constant [6 x i8] c" blk=\00", align 1
@.str.33 = private unnamed_addr constant [3 x i8] c"p2\00", align 1
@.str.34 = private unnamed_addr constant [4 x i8] c"p10\00", align 1
@.str.35 = private unnamed_addr constant [7 x i8] c"p10_p0\00", align 1
@.str.36 = private unnamed_addr constant [27 x i8] c"auth skipped: guard failed\00", align 1
@.str.37 = private unnamed_addr constant [33 x i8] c"pre auth_write: port=10 len=0x70\00", align 1
@.str.38 = private unnamed_addr constant [21 x i8] c"post auth_write: rc=\00", align 1
@.str.39 = private unnamed_addr constant [8 x i8] c" bytes=\00", align 1
@.str.40 = private unnamed_addr constant [36 x i8] c"pre auth_read: port=10 max_len=0x70\00", align 1
@.str.41 = private unnamed_addr constant [22 x i8] c"post auth_read: read=\00", align 1
@.str.42 = private unnamed_addr constant [9 x i8] c" stat=0x\00", align 1
@.str.43 = private unnamed_addr constant [8 x i8] c" flg=0x\00", align 1
@.str.44 = private unnamed_addr constant [6 x i8] c" vrd=\00", align 1
@.str.45 = private unnamed_addr constant [7 x i8] c"pio_16\00", align 1
@.str.46 = private unnamed_addr constant [6 x i8] c"pio_0\00", align 1
@.str.47 = private unnamed_addr constant [7 x i8] c"pio_17\00", align 1
@.str.48 = private unnamed_addr constant [7 x i8] c"dma_16\00", align 1
@.str.49 = private unnamed_addr constant [18 x i8] c"pre unmap: rgn=0x\00", align 1
@.str.50 = private unnamed_addr constant [14 x i8] c" len=0x100000\00", align 1
@.str.51 = private unnamed_addr constant [16 x i8] c"post unmap: rc=\00", align 1
@.str.52 = private unnamed_addr constant [17 x i8] c"pre free: rgn=0x\00", align 1
@.str.53 = private unnamed_addr constant [15 x i8] c"post free: rc=\00", align 1
@.str.54 = private unnamed_addr constant [23 x i8] c"pre close: bus=4 dev=2\00", align 1
@.str.55 = private unnamed_addr constant [16 x i8] c"post close: rc=\00", align 1
@.str.56 = private unnamed_addr constant [27 x i8] c"finish: ps2_netemu_p11_W1 \00", align 1
@.str.57 = private unnamed_addr constant [14 x i8] c"clean success\00", align 1
@.str.58 = private unnamed_addr constant [13 x i8] c"step failed=\00", align 1
@HEX_DIGITS = internal unnamed_addr constant [17 x i8] c"0123456789abcdef\00", align 1
@.str.59 = private unnamed_addr constant [11 x i8] c"pre vuart_\00", align 1
@.str.60 = private unnamed_addr constant [12 x i8] c"post vuart_\00", align 1
@.str.61 = private unnamed_addr constant [6 x i8] c": rc=\00", align 1
@.str.62 = private unnamed_addr constant [8 x i8] c" val=0x\00", align 1
@auth_verdict_to_str.STRS = internal unnamed_addr constant [7 x ptr] [ptr @.str.63, ptr @.str.64, ptr @.str.65, ptr @.str.66, ptr @.str.67, ptr @.str.68, ptr @.str.69], align 8
@.str.63 = private unnamed_addr constant [5 x i8] c"NONE\00", align 1
@.str.64 = private unnamed_addr constant [3 x i8] c"OK\00", align 1
@.str.65 = private unnamed_addr constant [9 x i8] c"ERR_STAT\00", align 1
@.str.66 = private unnamed_addr constant [8 x i8] c"TIMEOUT\00", align 1
@.str.67 = private unnamed_addr constant [6 x i8] c"SHORT\00", align 1
@.str.68 = private unnamed_addr constant [8 x i8] c"SKIPPED\00", align 1
@.str.69 = private unnamed_addr constant [10 x i8] c"WRITE_ERR\00", align 1
@.str.70 = private unnamed_addr constant [5 x i8] c"pre \00", align 1
@.str.71 = private unnamed_addr constant [7 x i8] c": lba=\00", align 1
@.str.72 = private unnamed_addr constant [8 x i8] c" proto=\00", align 1
@.str.73 = private unnamed_addr constant [7 x i8] c" blks=\00", align 1
@.str.74 = private unnamed_addr constant [6 x i8] c" bsz=\00", align 1
@.str.75 = private unnamed_addr constant [10 x i8] c"timeout: \00", align 1
@.str.76 = private unnamed_addr constant [31 x i8] c" timed out; halting hypercalls\00", align 1
@.str.77 = private unnamed_addr constant [6 x i8] c"post \00", align 1
@.str.78 = private unnamed_addr constant [6 x i8] c" cls=\00", align 1
@.str.79 = private unnamed_addr constant [5 x i8] c" a5=\00", align 1
@.str.80 = private unnamed_addr constant [5 x i8] c" w0=\00", align 1
@.str.81 = private unnamed_addr constant [6 x i8] c" w16=\00", align 1
@.str.82 = private unnamed_addr constant [7 x i8] c" vol='\00", align 1
@class_to_str.STRS = internal unnamed_addr constant [4 x ptr] [ptr @.str.83, ptr @.str.84, ptr @.str.85, ptr @.str.86], align 8
@.str.83 = private unnamed_addr constant [10 x i8] c"UNCHANGED\00", align 1
@.str.84 = private unnamed_addr constant [6 x i8] c"ZEROS\00", align 1
@.str.85 = private unnamed_addr constant [8 x i8] c"DATA_OK\00", align 1
@.str.86 = private unnamed_addr constant [6 x i8] c"OTHER\00", align 1
@.str.87 = private unnamed_addr constant [23 x i8] c"pre sense: cmd_lpar=0x\00", align 1
@.str.88 = private unnamed_addr constant [25 x i8] c"timeout: sense timed out\00", align 1
@.str.89 = private unnamed_addr constant [16 x i8] c"post sense: rc=\00", align 1
@.str.90 = private unnamed_addr constant [9 x i8] c" skey=0x\00", align 1
@.str.91 = private unnamed_addr constant [8 x i8] c" asc=0x\00", align 1
@.str.92 = private unnamed_addr constant [9 x i8] c" ascq=0x\00", align 1
@.str.93 = private unnamed_addr constant [14 x i8] c"P11-W1 AUTH: \00", align 1
@.str.94 = private unnamed_addr constant [7 x i8] c" ST=0x\00", align 1
@.str.95 = private unnamed_addr constant [7 x i8] c" FL=0x\00", align 1
@.str.96 = private unnamed_addr constant [15 x i8] c"P11-W1 PIO16: \00", align 1
@.str.97 = private unnamed_addr constant [7 x i8] c" PVD: \00", align 1
@.str.98 = private unnamed_addr constant [12 x i8] c"AUTH BYTES=\00", align 1
@.str.99 = private unnamed_addr constant [8 x i8] c" POLLS=\00", align 1
@.str.100 = private unnamed_addr constant [5 x i8] c" WR=\00", align 1
@.str.101 = private unnamed_addr constant [11 x i8] c"VUART: P2=\00", align 1
@.str.102 = private unnamed_addr constant [6 x i8] c" P10=\00", align 1
@.str.103 = private unnamed_addr constant [4 x i8] c" W=\00", align 1
@.str.104 = private unnamed_addr constant [4 x i8] c" R=\00", align 1
@.str.105 = private unnamed_addr constant [4 x i8] c"HC=\00", align 1
@.str.106 = private unnamed_addr constant [6 x i8] c" LOG=\00", align 1
@.str.107 = private unnamed_addr constant [7 x i8] c" SKIP=\00", align 1
@.str.108 = private unnamed_addr constant [8 x i8] c" TMO=0x\00", align 1
@.str.109 = private unnamed_addr constant [12 x i8] c"PIO: 16_A5=\00", align 1
@.str.110 = private unnamed_addr constant [7 x i8] c" 0_A5=\00", align 1
@.str.111 = private unnamed_addr constant [8 x i8] c" 17_A5=\00", align 1
@.str.112 = private unnamed_addr constant [14 x i8] c"CDVD LPAR: 0x\00", align 1
@.str.113 = private unnamed_addr constant [11 x i8] c"DMA RGN=0x\00", align 1
@.str.114 = private unnamed_addr constant [8 x i8] c" BUS=0x\00", align 1
@.str.115 = private unnamed_addr constant [15 x i8] c"P11-W1 RUNNING\00", align 1

; Function Attrs: minsize nounwind optsize
define dso_local signext range(i32 -1, 1) i32 @hddlog_init() local_unnamed_addr #0 {
  %1 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %2 = icmp eq i64 %1, 0
  br i1 %2, label %57, label %3

3:                                                ; preds = %0
  %4 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %5 = inttoptr i64 %4 to ptr
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 1668
  %7 = load volatile i32, ptr %6, align 4, !tbaa !12
  %8 = icmp eq i32 %7, 0
  br i1 %8, label %9, label %57

9:                                                ; preds = %3
  %10 = tail call i64 @native_clock() #9
  %11 = getelementptr inbounds nuw i8, ptr %5, i64 1784
  store volatile i64 %10, ptr %11, align 8, !tbaa !14
  %12 = getelementptr inbounds nuw i8, ptr %5, i64 1672
  store volatile i32 1, ptr %12, align 8, !tbaa !15
  %13 = getelementptr inbounds nuw i8, ptr %5, i64 1676
  store volatile i32 0, ptr %13, align 4, !tbaa !16
  %14 = tail call fastcc signext i32 @is_hdd_log_safe() #10
  %15 = icmp eq i32 %14, 0
  br i1 %15, label %16, label %19

16:                                               ; preds = %9
  store volatile i8 1, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  %17 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %18 = add i16 %17, 1
  store volatile i16 %18, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  store volatile i32 1, ptr %6, align 4, !tbaa !12
  br label %57

19:                                               ; preds = %9
  %20 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_init.path) #9
  %21 = icmp ugt i32 %20, 7
  br i1 %21, label %22, label %25

22:                                               ; preds = %19
  %23 = icmp eq i32 %20, -2
  %24 = select i1 %23, i8 2, i8 6
  store volatile i8 %24, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %57

25:                                               ; preds = %19, %42
  %26 = phi i64 [ %44, %42 ], [ 0, %19 ]
  %27 = icmp eq i64 %26, 64
  br i1 %27, label %28, label %42

28:                                               ; preds = %25
  store volatile i64 5640006764978326599, ptr %5, align 8, !tbaa !19
  %29 = getelementptr inbounds nuw i8, ptr %5, i64 8
  store volatile i32 65536, ptr %29, align 8, !tbaa !20
  %30 = getelementptr inbounds nuw i8, ptr %5, i64 12
  store volatile i32 512, ptr %30, align 4, !tbaa !20
  %31 = getelementptr inbounds nuw i8, ptr %5, i64 16
  store volatile i32 65536, ptr %31, align 8, !tbaa !20
  %32 = getelementptr inbounds nuw i8, ptr %5, i64 20
  store volatile i32 512, ptr %32, align 4, !tbaa !20
  %33 = getelementptr inbounds nuw i8, ptr %5, i64 24
  store volatile i32 127, ptr %33, align 8, !tbaa !20
  %34 = getelementptr inbounds nuw i8, ptr %5, i64 28
  store volatile i32 1, ptr %34, align 4, !tbaa !20
  %35 = load volatile i64, ptr %11, align 8, !tbaa !14
  %36 = getelementptr inbounds nuw i8, ptr %5, i64 32
  store volatile i64 %35, ptr %36, align 8, !tbaa !19
  %37 = getelementptr inbounds nuw i8, ptr %5, i64 40
  store volatile i32 0, ptr %37, align 8, !tbaa !20
  %38 = getelementptr inbounds nuw i8, ptr %5, i64 44
  store volatile i32 0, ptr %38, align 4, !tbaa !20
  %39 = tail call i64 @stock_raw_write(i32 noundef signext %20, i64 noundef 0, ptr noundef nonnull %5, i64 noundef 512) #9
  %40 = icmp eq i64 %39, 512
  %41 = tail call signext i32 @stock_ufs_close(i32 noundef signext %20) #9
  br i1 %40, label %46, label %45

42:                                               ; preds = %25
  %43 = getelementptr inbounds nuw [8 x i8], ptr %5, i64 %26
  store volatile i64 0, ptr %43, align 8, !tbaa !19
  %44 = add nuw nsw i64 %26, 1
  br label %25, !llvm.loop !21

45:                                               ; preds = %28
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %57

46:                                               ; preds = %28
  %47 = icmp eq i32 %41, 0
  br i1 %47, label %49, label %48

48:                                               ; preds = %46
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %57

49:                                               ; preds = %46
  %50 = tail call fastcc signext i32 @is_hdd_log_safe() #10
  %51 = icmp eq i32 %50, 0
  br i1 %51, label %56, label %52

52:                                               ; preds = %49
  %53 = tail call signext i32 @stock_hdd_cache_flush() #9
  %54 = icmp eq i32 %53, 0
  br i1 %54, label %56, label %55

55:                                               ; preds = %52
  store volatile i8 7, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %57

56:                                               ; preds = %52, %49
  store volatile i32 1, ptr %6, align 4, !tbaa !12
  br label %57

57:                                               ; preds = %55, %16, %3, %45, %56, %48, %22, %0
  %58 = phi i32 [ -1, %0 ], [ -1, %16 ], [ 0, %3 ], [ -1, %22 ], [ -1, %45 ], [ -1, %48 ], [ 0, %56 ], [ -1, %55 ]
  ret i32 %58
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: minsize optsize
declare i64 @native_clock() local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc signext range(i32 0, 2) i32 @is_hdd_log_safe() unnamed_addr #3 {
  %1 = load i8, ptr inttoptr (i64 37865685 to ptr), align 1, !tbaa !23
  %2 = load i8, ptr inttoptr (i64 37865672 to ptr), align 8, !tbaa !23
  %3 = load volatile i64, ptr inttoptr (i64 37865568 to ptr), align 32, !tbaa !19
  %4 = load volatile i64, ptr inttoptr (i64 37865608 to ptr), align 8, !tbaa !19
  %5 = load volatile i64, ptr inttoptr (i64 37865616 to ptr), align 16, !tbaa !19
  %6 = load volatile i64, ptr inttoptr (i64 37865624 to ptr), align 8, !tbaa !19
  %7 = icmp eq i8 %1, 1
  %8 = icmp eq i8 %2, 0
  %9 = select i1 %7, i1 %8, i1 false
  %10 = icmp eq i64 %3, 3
  %11 = select i1 %9, i1 %10, i1 false
  %12 = icmp eq i64 %6, 0
  %13 = select i1 %11, i1 %12, i1 false
  %14 = icmp eq i64 %4, 0
  %15 = select i1 %13, i1 %14, i1 false
  %16 = icmp eq i64 %5, 0
  %17 = select i1 %15, i1 %16, i1 false
  br i1 %17, label %18, label %22

18:                                               ; preds = %0
  %19 = load i32, ptr inttoptr (i64 50680192 to ptr), align 128, !tbaa !20
  %20 = icmp eq i32 %19, 0
  %21 = zext i1 %20 to i32
  br label %22

22:                                               ; preds = %18, %0
  %23 = phi i32 [ %21, %18 ], [ 0, %0 ]
  ret i32 %23
}

; Function Attrs: minsize optsize
declare signext i32 @stock_ufs_open(i64 noundef, ptr noundef) local_unnamed_addr #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize optsize
declare i64 @stock_raw_write(i32 noundef signext, i64 noundef, ptr noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare signext i32 @stock_ufs_close(i32 noundef signext) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare signext i32 @stock_hdd_cache_flush() local_unnamed_addr #2

; Function Attrs: minsize nounwind optsize
define dso_local signext range(i32 -1, 1) i32 @hddlog_write(i32 noundef zeroext %0, i64 noundef %1, i64 noundef %2, ptr nofree noundef readonly captures(address_is_null) %3) local_unnamed_addr #0 {
  %5 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %6 = icmp eq i64 %5, 0
  br i1 %6, label %106, label %7

7:                                                ; preds = %4
  %8 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %9 = inttoptr i64 %8 to ptr
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 1668
  %11 = load volatile i32, ptr %10, align 4, !tbaa !12
  %12 = icmp eq i32 %11, 0
  br i1 %12, label %106, label %13

13:                                               ; preds = %7
  %14 = getelementptr inbounds nuw i8, ptr %9, i64 1672
  %15 = load volatile i32, ptr %14, align 8, !tbaa !15
  %16 = icmp ugt i32 %15, 127
  br i1 %16, label %17, label %18

17:                                               ; preds = %13
  store volatile i8 8, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

18:                                               ; preds = %13
  %19 = tail call fastcc signext i32 @is_hdd_log_safe() #10
  %20 = icmp eq i32 %19, 0
  br i1 %20, label %21, label %24

21:                                               ; preds = %18
  %22 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %23 = add i16 %22, 1
  store volatile i16 %23, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  br label %106

24:                                               ; preds = %18
  %25 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_write.path) #9
  %26 = icmp ugt i32 %25, 7
  br i1 %26, label %27, label %30

27:                                               ; preds = %24
  %28 = icmp eq i32 %25, -2
  %29 = select i1 %28, i8 2, i8 6
  store volatile i8 %29, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

30:                                               ; preds = %24
  %31 = getelementptr inbounds nuw i8, ptr %9, i64 512
  br label %32

32:                                               ; preds = %70, %30
  %33 = phi i64 [ %72, %70 ], [ 0, %30 ]
  %34 = icmp eq i64 %33, 64
  br i1 %34, label %35, label %70

35:                                               ; preds = %32
  %36 = getelementptr inbounds nuw i8, ptr %9, i64 1676
  %37 = load volatile i32, ptr %36, align 4, !tbaa !16
  %38 = add i32 %37, 1
  store volatile i32 %38, ptr %36, align 4, !tbaa !16
  store volatile i32 1280264018, ptr %31, align 8, !tbaa !20
  %39 = load volatile i32, ptr %36, align 4, !tbaa !16
  %40 = getelementptr inbounds nuw i8, ptr %9, i64 516
  store volatile i32 %39, ptr %40, align 4, !tbaa !20
  %41 = getelementptr inbounds nuw i8, ptr %9, i64 520
  store volatile i32 %0, ptr %41, align 8, !tbaa !20
  %42 = getelementptr inbounds nuw i8, ptr %9, i64 524
  store volatile i32 0, ptr %42, align 4, !tbaa !20
  %43 = tail call i64 @native_clock() #9
  %44 = getelementptr inbounds nuw i8, ptr %9, i64 528
  store volatile i64 %43, ptr %44, align 8, !tbaa !19
  %45 = getelementptr inbounds nuw i8, ptr %9, i64 536
  store volatile i64 %1, ptr %45, align 8, !tbaa !19
  %46 = getelementptr inbounds nuw i8, ptr %9, i64 544
  store volatile i64 %2, ptr %46, align 8, !tbaa !19
  %47 = getelementptr inbounds nuw i8, ptr %9, i64 1784
  %48 = load volatile i64, ptr %47, align 8, !tbaa !14
  %49 = getelementptr inbounds nuw i8, ptr %9, i64 552
  store volatile i64 %48, ptr %49, align 8, !tbaa !19
  %50 = getelementptr inbounds nuw i8, ptr %9, i64 584
  %51 = icmp eq ptr %3, null
  br i1 %51, label %62, label %52

52:                                               ; preds = %35, %59
  %53 = phi i64 [ %60, %59 ], [ 0, %35 ]
  %54 = getelementptr inbounds nuw i8, ptr %3, i64 %53
  %55 = load i8, ptr %54, align 1, !tbaa !23
  %56 = icmp ne i8 %55, 0
  %57 = icmp samesign ult i64 %53, 439
  %58 = and i1 %57, %56
  br i1 %58, label %59, label %62

59:                                               ; preds = %52
  %60 = add nuw nsw i64 %53, 1
  %61 = getelementptr inbounds nuw i8, ptr %50, i64 %53
  store i8 %55, ptr %61, align 1, !tbaa !23
  br label %52, !llvm.loop !24

62:                                               ; preds = %52, %35
  %63 = phi i64 [ 0, %35 ], [ %53, %52 ]
  %64 = getelementptr inbounds nuw i8, ptr %50, i64 %63
  store i8 0, ptr %64, align 1, !tbaa !23
  %65 = load volatile i32, ptr %14, align 8, !tbaa !15
  %66 = zext i32 %65 to i64
  %67 = shl nuw nsw i64 %66, 9
  %68 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef %67, ptr noundef nonnull %31, i64 noundef 512) #9
  %69 = icmp eq i64 %68, 512
  br i1 %69, label %75, label %73

70:                                               ; preds = %32
  %71 = getelementptr inbounds nuw [8 x i8], ptr %31, i64 %33
  store volatile i64 0, ptr %71, align 8, !tbaa !19
  %72 = add nuw nsw i64 %33, 1
  br label %32, !llvm.loop !25

73:                                               ; preds = %62
  %74 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #9
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

75:                                               ; preds = %62
  %76 = load volatile i32, ptr %14, align 8, !tbaa !15
  %77 = add i32 %76, 1
  %78 = getelementptr inbounds nuw i8, ptr %9, i64 28
  store volatile i32 %77, ptr %78, align 4, !tbaa !20
  %79 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !26
  %80 = add i32 %79, 1
  %81 = getelementptr inbounds nuw i8, ptr %9, i64 44
  store volatile i32 %80, ptr %81, align 4, !tbaa !20
  %82 = icmp eq i32 %0, 1162757152
  br i1 %82, label %83, label %85

83:                                               ; preds = %75
  %84 = getelementptr inbounds nuw i8, ptr %9, i64 40
  store volatile i32 1, ptr %84, align 8, !tbaa !20
  store volatile i8 1, ptr inttoptr (i64 9637743 to ptr), align 1, !tbaa !27
  br label %85

85:                                               ; preds = %83, %75
  %86 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef 0, ptr noundef nonnull %9, i64 noundef 512) #9
  %87 = icmp eq i64 %86, 512
  %88 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #9
  br i1 %87, label %90, label %89

89:                                               ; preds = %85
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

90:                                               ; preds = %85
  %91 = icmp eq i32 %88, 0
  br i1 %91, label %93, label %92

92:                                               ; preds = %90
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

93:                                               ; preds = %90
  %94 = tail call fastcc signext i32 @is_hdd_log_safe() #10
  %95 = icmp eq i32 %94, 0
  br i1 %95, label %96, label %99

96:                                               ; preds = %93
  %97 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %98 = add i16 %97, 1
  store volatile i16 %98, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  br label %106

99:                                               ; preds = %93
  %100 = tail call signext i32 @stock_hdd_cache_flush() #9
  %101 = icmp eq i32 %100, 0
  br i1 %101, label %103, label %102

102:                                              ; preds = %99
  store volatile i8 7, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

103:                                              ; preds = %99
  store volatile i32 %77, ptr %14, align 8, !tbaa !15
  %104 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !26
  %105 = add i32 %104, 1
  store volatile i32 %105, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !26
  br label %106

106:                                              ; preds = %17, %21, %7, %73, %92, %96, %103, %102, %89, %27, %4
  %107 = phi i32 [ -1, %4 ], [ -1, %17 ], [ -1, %7 ], [ 0, %21 ], [ -1, %27 ], [ -1, %73 ], [ -1, %89 ], [ -1, %92 ], [ 0, %96 ], [ -1, %102 ], [ 0, %103 ]
  ret i32 %107
}

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i32 noundef zeroext %0) local_unnamed_addr #0 {
  %2 = alloca ptr, align 8
  %3 = alloca [256 x i8], align 1
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = icmp ugt i32 %0, 8
  %10 = select i1 %9, i32 0, i32 %0
  %11 = tail call fastcc ptr @get_arena() #10
  %12 = icmp eq ptr %11, null
  br i1 %12, label %13, label %36

13:                                               ; preds = %1
  %14 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %15 = and i32 %14, 8
  %16 = icmp eq i32 %15, 0
  br i1 %16, label %17, label %674

17:                                               ; preds = %13
  %18 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %19 = or i32 %18, 1
  store volatile i32 %19, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %20 = tail call i64 @native_alloc(i64 noundef 4096, i64 noundef 3, i64 noundef 0) #9
  %21 = tail call fastcc signext i32 @arena_rw(i64 noundef %20) #10
  %22 = icmp eq i32 %21, 0
  br i1 %22, label %33, label %23

23:                                               ; preds = %17
  store volatile i64 %20, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %24 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %25 = or i32 %24, 4
  store volatile i32 %25, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %26 = inttoptr i64 %20 to ptr
  br label %27

27:                                               ; preds = %30, %23
  %28 = phi i64 [ %32, %30 ], [ 0, %23 ]
  %29 = icmp eq i64 %28, 2112
  br i1 %29, label %36, label %30

30:                                               ; preds = %27
  %31 = getelementptr inbounds nuw i8, ptr %26, i64 %28
  store volatile i8 0, ptr %31, align 1, !tbaa !23
  %32 = add nuw nsw i64 %28, 1
  br label %27, !llvm.loop !29

33:                                               ; preds = %17
  %34 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %35 = or i32 %34, 8
  store volatile i32 %35, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  br label %674

36:                                               ; preds = %27, %1
  %37 = phi ptr [ %11, %1 ], [ %26, %27 ]
  %38 = tail call i64 @native_clock() #9
  %39 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !30
  store volatile i64 %38, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !30
  %40 = icmp ne i64 %39, 0
  %41 = sub i64 %38, %39
  %42 = icmp ugt i64 %41, 119700000
  %43 = select i1 %40, i1 %42, i1 false
  br i1 %43, label %44, label %47

44:                                               ; preds = %36
  %45 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !31
  %46 = add i32 %45, 1
  store volatile i32 %46, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !31
  br label %47

47:                                               ; preds = %44, %36
  %48 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %49 = and i32 %48, 2
  %50 = icmp eq i32 %49, 0
  br i1 %50, label %51, label %577

51:                                               ; preds = %47
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #11
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #11
  %52 = tail call signext i32 @hddlog_init() #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str) #10
  %53 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %53, align 1, !tbaa !23
  %54 = call signext i32 @hddlog_write(i32 noundef zeroext 1112493908, i64 noundef 2112, i64 noundef 1, ptr noundef nonnull %3) #10
  %55 = getelementptr inbounds nuw i8, ptr %37, i64 1660
  br label %56

56:                                               ; preds = %95, %51
  %57 = phi i64 [ 0, %51 ], [ %100, %95 ]
  %58 = phi i32 [ 0, %51 ], [ %96, %95 ]
  %59 = phi i64 [ 2, %51 ], [ %97, %95 ]
  %60 = phi i32 [ 0, %51 ], [ %98, %95 ]
  %61 = phi i32 [ 0, %51 ], [ %99, %95 ]
  %62 = icmp eq i64 %57, 8
  br i1 %62, label %63, label %79

63:                                               ; preds = %56
  %64 = getelementptr inbounds nuw i8, ptr %37, i64 1664
  store volatile i32 %58, ptr %64, align 8, !tbaa !35
  store volatile i32 %61, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !36
  store volatile i32 %60, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !37
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.1) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %61) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.2) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %60) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.3) #10
  %65 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %65, align 1, !tbaa !23
  %66 = zext i32 %61 to i64
  %67 = zext nneg i32 %60 to i64
  %68 = call signext i32 @hddlog_write(i32 noundef zeroext 1396916558, i64 noundef %66, i64 noundef %67, ptr noundef nonnull %3) #10
  %69 = load volatile i64, ptr inttoptr (i64 38110264 to ptr), align 8, !tbaa !19
  %70 = load volatile i64, ptr inttoptr (i64 38110248 to ptr), align 8, !tbaa !19
  %71 = load volatile i64, ptr inttoptr (i64 38110256 to ptr), align 16, !tbaa !19
  %72 = and i64 %69, 281470682791935
  %73 = icmp ne i64 %72, 87960930222080
  %74 = and i64 %70, -2146435073
  %75 = icmp ne i64 %74, 2147483648
  %76 = select i1 %73, i1 true, i1 %75
  %77 = icmp ult i64 %71, 524288
  %78 = select i1 %76, i1 true, i1 %77
  br i1 %78, label %101, label %104

79:                                               ; preds = %56
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #11
  store i64 0, ptr %5, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #11
  store i64 0, ptr %6, align 8, !tbaa !19
  %80 = or disjoint i64 %57, 7234318118812647424
  %81 = call i64 @repo_read(ptr noundef nonnull %5, ptr noundef nonnull %6, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8392862959675637760, i64 noundef 0) #9
  %82 = icmp eq i64 %81, 0
  br i1 %82, label %83, label %95

83:                                               ; preds = %79
  %84 = add i32 %58, 1
  %85 = load i64, ptr %5, align 8, !tbaa !19
  switch i64 %85, label %95 [
    i64 5, label %86
    i64 0, label %94
  ]

86:                                               ; preds = %83
  %87 = add i32 %61, 1
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #11
  store i64 0, ptr %7, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #11
  store i64 0, ptr %8, align 8, !tbaa !19
  %88 = call i64 @repo_read(ptr noundef nonnull %7, ptr noundef nonnull %8, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8243108395510267904, i64 noundef 0) #9
  %89 = icmp eq i64 %88, 0
  br i1 %89, label %90, label %93

90:                                               ; preds = %86
  %91 = load i64, ptr %7, align 8, !tbaa !19
  %92 = trunc i64 %91 to i32
  store volatile i32 %92, ptr %55, align 4, !tbaa !38
  br label %93

93:                                               ; preds = %90, %86
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #11
  br label %95

94:                                               ; preds = %83
  br label %95

95:                                               ; preds = %94, %93, %83, %79
  %96 = phi i32 [ %84, %93 ], [ %84, %94 ], [ %84, %83 ], [ %58, %79 ]
  %97 = phi i64 [ %57, %93 ], [ %59, %94 ], [ %59, %83 ], [ %59, %79 ]
  %98 = phi i32 [ %60, %93 ], [ 1, %94 ], [ %60, %83 ], [ %60, %79 ]
  %99 = phi i32 [ %87, %93 ], [ %61, %94 ], [ %61, %83 ], [ %61, %79 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #11
  %100 = add nuw nsw i64 %57, 1
  br label %56, !llvm.loop !39

101:                                              ; preds = %63
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 -1, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.4) #10
  %102 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %102, align 1, !tbaa !23
  %103 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.5) #10
  br label %568

104:                                              ; preds = %63
  %105 = getelementptr inbounds nuw i8, ptr %37, i64 1760
  store volatile i64 %69, ptr %105, align 8, !tbaa !42
  %106 = getelementptr inbounds nuw i8, ptr %37, i64 1768
  store volatile i64 %70, ptr %106, align 8, !tbaa !43
  %107 = getelementptr inbounds nuw i8, ptr %37, i64 1776
  store volatile i64 %71, ptr %107, align 8, !tbaa !44
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.6) #10
  %108 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %108, align 1, !tbaa !23
  %109 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.7) #10
  %110 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %110, align 1, !tbaa !23
  %111 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #10
  %112 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %113 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %114 = add i32 %113, 1
  store volatile i32 %114, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %115 = trunc i64 %112 to i32
  %116 = getelementptr inbounds nuw i8, ptr %37, i64 1604
  store volatile i32 %115, ptr %116, align 4, !tbaa !46
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.8) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %115) #10
  %117 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %117, align 1, !tbaa !23
  %118 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %112, i64 noundef 0, ptr noundef nonnull %3) #10
  %119 = icmp eq i64 %112, 0
  br i1 %119, label %121, label %120

120:                                              ; preds = %104
  store volatile i32 2, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 %115, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %562

121:                                              ; preds = %104
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.9) #10
  %122 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %122, align 1, !tbaa !23
  %123 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 1048576, i64 noundef 20, ptr noundef nonnull %3) #10
  %124 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef %59, i64 noundef 1048576, i64 noundef 20, i64 noundef 0, i64 noundef 0) #9
  %125 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %126 = add i32 %125, 1
  store volatile i32 %126, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %127 = trunc i64 %124 to i32
  %128 = getelementptr inbounds nuw i8, ptr %37, i64 1608
  store volatile i32 %127, ptr %128, align 8, !tbaa !47
  %129 = icmp eq i64 %124, 0
  br i1 %129, label %133, label %130

130:                                              ; preds = %121
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.10) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %127) #10
  %131 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %131, align 1, !tbaa !23
  %132 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %124, i64 noundef 0, ptr noundef nonnull %3) #10
  store volatile i32 3, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 %127, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %552

133:                                              ; preds = %121
  %134 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %135 = getelementptr inbounds nuw i8, ptr %37, i64 1744
  store volatile i64 %134, ptr %135, align 8, !tbaa !49
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.11) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %134) #10
  %136 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %136, align 1, !tbaa !23
  %137 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef 0, i64 noundef %134, ptr noundef nonnull %3) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.12) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %69) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.13) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %134) #10
  %138 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %138, align 1, !tbaa !23
  %139 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %69, i64 noundef %134, ptr noundef nonnull %3) #10
  %140 = call i64 @lv1_hcall(i64 noundef 176, i64 noundef 4, i64 noundef %59, i64 noundef %69, i64 noundef %134, i64 noundef 1048576, i64 noundef -2305843009213691904) #9
  %141 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %142 = add i32 %141, 1
  store volatile i32 %142, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %143 = trunc i64 %140 to i32
  %144 = getelementptr inbounds nuw i8, ptr %37, i64 1612
  store volatile i32 %143, ptr %144, align 4, !tbaa !50
  %145 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %146 = getelementptr inbounds nuw i8, ptr %37, i64 1752
  store volatile i64 %145, ptr %146, align 8, !tbaa !51
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.14) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %143) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.15) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %145) #10
  %147 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %147, align 1, !tbaa !23
  %148 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %140, i64 noundef %145, ptr noundef nonnull %3) #10
  %149 = icmp eq i64 %140, 0
  br i1 %149, label %151, label %150

150:                                              ; preds = %133
  store volatile i32 4, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 %143, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %542

151:                                              ; preds = %133
  %152 = inttoptr i64 %70 to ptr
  %153 = or disjoint i64 %70, 4096
  %154 = inttoptr i64 %153 to ptr
  %155 = or disjoint i64 %69, 4096
  call fastcc void @setup_atapi_block(ptr noundef %152, i8 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i64 noundef 0) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.16) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %69) #10
  %156 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %156, align 1, !tbaa !23
  %157 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %69, i64 noundef 0, ptr noundef nonnull %3) #10
  %158 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %59, i64 noundef 1, i64 noundef %69, i64 noundef 64, i64 noundef 0, i64 noundef 0) #9
  %159 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %160 = add i32 %159, 1
  store volatile i32 %160, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %161 = trunc i64 %158 to i32
  %162 = getelementptr inbounds nuw i8, ptr %37, i64 1628
  store volatile i32 %161, ptr %162, align 4, !tbaa !52
  %163 = icmp eq i64 %158, 0
  br i1 %163, label %164, label %179

164:                                              ; preds = %151
  %165 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %166 = getelementptr inbounds nuw i8, ptr %37, i64 1792
  %167 = getelementptr inbounds nuw i8, ptr %37, i64 1680
  %168 = getelementptr inbounds nuw i8, ptr %37, i64 1856
  %169 = call fastcc signext i32 @poll_completion(i64 noundef %59, i64 noundef %165, ptr noundef nonnull %166, ptr noundef nonnull %167, ptr noundef nonnull %168) #10
  %170 = icmp eq i32 %169, 0
  br i1 %170, label %187, label %171

171:                                              ; preds = %164
  %172 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  %173 = or i32 %172, 1
  store volatile i32 %173, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  store volatile i32 5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.17) #10
  %174 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %174, align 1, !tbaa !23
  %175 = load volatile i32, ptr %167, align 8, !tbaa !54
  %176 = zext i32 %175 to i64
  %177 = load volatile i64, ptr %168, align 8, !tbaa !55
  %178 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %176, i64 noundef %177, ptr noundef nonnull %3) #10
  br label %562

179:                                              ; preds = %151
  %180 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %181 = icmp eq i32 %180, 0
  br i1 %181, label %182, label %183

182:                                              ; preds = %179
  store volatile i32 5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  br label %183

183:                                              ; preds = %182, %179
  %184 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  %185 = icmp eq i32 %184, 0
  br i1 %185, label %186, label %187

186:                                              ; preds = %183
  store volatile i32 %161, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %187

187:                                              ; preds = %186, %183, %164
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.18) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %161) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.19) #10
  %188 = getelementptr inbounds nuw i8, ptr %37, i64 1792
  %189 = load volatile i64, ptr %188, align 8, !tbaa !56
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %189) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.20) #10
  %190 = getelementptr inbounds nuw i8, ptr %37, i64 1680
  %191 = load volatile i32, ptr %190, align 8, !tbaa !54
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %191) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.21) #10
  %192 = getelementptr inbounds nuw i8, ptr %37, i64 1856
  %193 = load volatile i64, ptr %192, align 8, !tbaa !55
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %193) #10
  %194 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %194, align 1, !tbaa !23
  %195 = load volatile i64, ptr %188, align 8, !tbaa !56
  %196 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %158, i64 noundef %195, ptr noundef nonnull %3) #10
  call fastcc void @setup_atapi_block(ptr noundef %152, i8 noundef zeroext 18, i32 noundef zeroext 36, i32 noundef zeroext 1, i32 noundef zeroext 1, i64 noundef %155) #10
  call fastcc void @prefill_buffer(ptr noundef nonnull %154, i32 noundef zeroext 36, i8 noundef zeroext 0) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.22) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %69) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.23) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %155) #10
  %197 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %197, align 1, !tbaa !23
  %198 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %69, i64 noundef %155, ptr noundef nonnull %3) #10
  %199 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %59, i64 noundef 1, i64 noundef %69, i64 noundef 64, i64 noundef %155, i64 noundef 36) #9
  %200 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %201 = add i32 %200, 1
  store volatile i32 %201, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %202 = trunc i64 %199 to i32
  %203 = getelementptr inbounds nuw i8, ptr %37, i64 1632
  store volatile i32 %202, ptr %203, align 8, !tbaa !57
  %204 = icmp eq i64 %199, 0
  br i1 %204, label %205, label %230

205:                                              ; preds = %187
  %206 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %207 = getelementptr inbounds nuw i8, ptr %37, i64 1800
  %208 = getelementptr inbounds nuw i8, ptr %37, i64 1684
  %209 = getelementptr inbounds nuw i8, ptr %37, i64 1864
  %210 = call fastcc signext i32 @poll_completion(i64 noundef %59, i64 noundef %206, ptr noundef nonnull %207, ptr noundef nonnull %208, ptr noundef nonnull %209) #10
  %211 = icmp eq i32 %210, 0
  br i1 %211, label %212, label %222

212:                                              ; preds = %205
  %213 = getelementptr inbounds nuw i8, ptr %37, i64 1920
  br label %214

214:                                              ; preds = %217, %212
  %215 = phi i64 [ 0, %212 ], [ %221, %217 ]
  %216 = icmp eq i64 %215, 36
  br i1 %216, label %238, label %217

217:                                              ; preds = %214
  %218 = getelementptr inbounds nuw i8, ptr %154, i64 %215
  %219 = load volatile i8, ptr %218, align 1, !tbaa !23
  %220 = getelementptr inbounds nuw i8, ptr %213, i64 %215
  store volatile i8 %219, ptr %220, align 1, !tbaa !23
  %221 = add nuw nsw i64 %215, 1
  br label %214, !llvm.loop !58

222:                                              ; preds = %205
  %223 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  %224 = or i32 %223, 2
  store volatile i32 %224, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  store volatile i32 6, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.24) #10
  %225 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %225, align 1, !tbaa !23
  %226 = load volatile i32, ptr %208, align 4, !tbaa !59
  %227 = zext i32 %226 to i64
  %228 = load volatile i64, ptr %209, align 8, !tbaa !60
  %229 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %227, i64 noundef %228, ptr noundef nonnull %3) #10
  br label %562

230:                                              ; preds = %187
  %231 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %232 = icmp eq i32 %231, 0
  br i1 %232, label %233, label %234

233:                                              ; preds = %230
  store volatile i32 6, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  br label %234

234:                                              ; preds = %233, %230
  %235 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  %236 = icmp eq i32 %235, 0
  br i1 %236, label %237, label %238

237:                                              ; preds = %234
  store volatile i32 %202, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %238

238:                                              ; preds = %214, %237, %234
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.25) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %202) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.19) #10
  %239 = getelementptr inbounds nuw i8, ptr %37, i64 1800
  %240 = load volatile i64, ptr %239, align 8, !tbaa !61
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %240) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.26) #10
  %241 = getelementptr inbounds nuw i8, ptr %154, i64 8
  call fastcc void @format_ascii(ptr noundef %4, ptr noundef nonnull %241, i32 noundef zeroext 16) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.27) #10
  %242 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %242, align 1, !tbaa !23
  %243 = load volatile i64, ptr %239, align 8, !tbaa !61
  %244 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %199, i64 noundef %243, ptr noundef nonnull %3) #10
  call fastcc void @setup_atapi_block(ptr noundef %152, i8 noundef zeroext 37, i32 noundef zeroext 8, i32 noundef zeroext 1, i32 noundef zeroext 1, i64 noundef %155) #10
  call fastcc void @prefill_buffer(ptr noundef nonnull %154, i32 noundef zeroext 8, i8 noundef zeroext 0) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.28) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %69) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.23) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %155) #10
  %245 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %245, align 1, !tbaa !23
  %246 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %69, i64 noundef %155, ptr noundef nonnull %3) #10
  %247 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %59, i64 noundef 1, i64 noundef %69, i64 noundef 64, i64 noundef %155, i64 noundef 8) #9
  %248 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %249 = add i32 %248, 1
  store volatile i32 %249, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %250 = trunc i64 %247 to i32
  %251 = getelementptr inbounds nuw i8, ptr %37, i64 1636
  store volatile i32 %250, ptr %251, align 4, !tbaa !62
  %252 = icmp eq i64 %247, 0
  br i1 %252, label %253, label %306

253:                                              ; preds = %238
  %254 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %255 = getelementptr inbounds nuw i8, ptr %37, i64 1808
  %256 = getelementptr inbounds nuw i8, ptr %37, i64 1688
  %257 = getelementptr inbounds nuw i8, ptr %37, i64 1872
  %258 = call fastcc signext i32 @poll_completion(i64 noundef %59, i64 noundef %254, ptr noundef nonnull %255, ptr noundef nonnull %256, ptr noundef nonnull %257) #10
  %259 = icmp eq i32 %258, 0
  br i1 %259, label %260, label %298

260:                                              ; preds = %253
  %261 = load volatile i8, ptr %154, align 1, !tbaa !23
  %262 = zext i8 %261 to i32
  %263 = shl nuw i32 %262, 24
  %264 = getelementptr inbounds nuw i8, ptr %154, i64 1
  %265 = load volatile i8, ptr %264, align 1, !tbaa !23
  %266 = zext i8 %265 to i32
  %267 = shl nuw nsw i32 %266, 16
  %268 = or disjoint i32 %267, %263
  %269 = getelementptr inbounds nuw i8, ptr %154, i64 2
  %270 = load volatile i8, ptr %269, align 1, !tbaa !23
  %271 = zext i8 %270 to i32
  %272 = shl nuw nsw i32 %271, 8
  %273 = or disjoint i32 %268, %272
  %274 = getelementptr inbounds nuw i8, ptr %154, i64 3
  %275 = load volatile i8, ptr %274, align 1, !tbaa !23
  %276 = zext i8 %275 to i32
  %277 = or disjoint i32 %273, %276
  %278 = getelementptr inbounds nuw i8, ptr %37, i64 1712
  store volatile i32 %277, ptr %278, align 8, !tbaa !63
  %279 = getelementptr inbounds nuw i8, ptr %154, i64 4
  %280 = load volatile i8, ptr %279, align 1, !tbaa !23
  %281 = zext i8 %280 to i32
  %282 = shl nuw i32 %281, 24
  %283 = getelementptr inbounds nuw i8, ptr %154, i64 5
  %284 = load volatile i8, ptr %283, align 1, !tbaa !23
  %285 = zext i8 %284 to i32
  %286 = shl nuw nsw i32 %285, 16
  %287 = or disjoint i32 %286, %282
  %288 = getelementptr inbounds nuw i8, ptr %154, i64 6
  %289 = load volatile i8, ptr %288, align 1, !tbaa !23
  %290 = zext i8 %289 to i32
  %291 = shl nuw nsw i32 %290, 8
  %292 = or disjoint i32 %287, %291
  %293 = getelementptr inbounds nuw i8, ptr %154, i64 7
  %294 = load volatile i8, ptr %293, align 1, !tbaa !23
  %295 = zext i8 %294 to i32
  %296 = or disjoint i32 %292, %295
  %297 = getelementptr inbounds nuw i8, ptr %37, i64 1716
  store volatile i32 %296, ptr %297, align 4, !tbaa !64
  br label %314

298:                                              ; preds = %253
  %299 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  %300 = or i32 %299, 4
  store volatile i32 %300, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  store volatile i32 7, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.29) #10
  %301 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %301, align 1, !tbaa !23
  %302 = load volatile i32, ptr %256, align 8, !tbaa !65
  %303 = zext i32 %302 to i64
  %304 = load volatile i64, ptr %257, align 8, !tbaa !66
  %305 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %303, i64 noundef %304, ptr noundef nonnull %3) #10
  br label %562

306:                                              ; preds = %238
  %307 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %308 = icmp eq i32 %307, 0
  br i1 %308, label %309, label %310

309:                                              ; preds = %306
  store volatile i32 7, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  br label %310

310:                                              ; preds = %309, %306
  %311 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  %312 = icmp eq i32 %311, 0
  br i1 %312, label %313, label %314

313:                                              ; preds = %310
  store volatile i32 %250, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %314

314:                                              ; preds = %313, %310, %260
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.30) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %250) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.19) #10
  %315 = getelementptr inbounds nuw i8, ptr %37, i64 1808
  %316 = load volatile i64, ptr %315, align 8, !tbaa !67
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %316) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.31) #10
  %317 = getelementptr inbounds nuw i8, ptr %37, i64 1712
  %318 = load volatile i32, ptr %317, align 8, !tbaa !63
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %318) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.32) #10
  %319 = getelementptr inbounds nuw i8, ptr %37, i64 1716
  %320 = load volatile i32, ptr %319, align 4, !tbaa !64
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %320) #10
  %321 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %321, align 1, !tbaa !23
  %322 = load volatile i64, ptr %315, align 8, !tbaa !67
  %323 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %247, i64 noundef %322, ptr noundef nonnull %3) #10
  %324 = getelementptr inbounds nuw i8, ptr %37, i64 2008
  %325 = getelementptr inbounds nuw i8, ptr %37, i64 2032
  call fastcc void @query_vuart_param(i64 noundef 2, i64 noundef 3, ptr noundef nonnull %324, ptr noundef nonnull %325, ptr noundef nonnull @.str.33) #10
  %326 = getelementptr inbounds nuw i8, ptr %37, i64 2012
  %327 = getelementptr inbounds nuw i8, ptr %37, i64 2040
  call fastcc void @query_vuart_param(i64 noundef 10, i64 noundef 3, ptr noundef nonnull %326, ptr noundef nonnull %327, ptr noundef nonnull @.str.34) #10
  %328 = load volatile i32, ptr %326, align 4, !tbaa !68
  %329 = sext i32 %328 to i64
  %330 = getelementptr inbounds nuw i8, ptr %37, i64 2016
  %331 = getelementptr inbounds nuw i8, ptr %37, i64 2048
  call fastcc void @query_vuart_param(i64 noundef 10, i64 noundef 0, ptr noundef nonnull %330, ptr noundef nonnull %331, ptr noundef nonnull @.str.35) #10
  br i1 %163, label %332, label %335

332:                                              ; preds = %314
  %333 = load volatile i64, ptr %188, align 8, !tbaa !56
  %334 = icmp eq i64 %333, 0
  br i1 %334, label %336, label %335

335:                                              ; preds = %332, %314
  br label %336

336:                                              ; preds = %335, %332
  %337 = phi i32 [ 0, %335 ], [ 1, %332 ]
  br i1 %252, label %338, label %341

338:                                              ; preds = %336
  %339 = load volatile i64, ptr %315, align 8, !tbaa !67
  %340 = icmp eq i64 %339, 0
  br i1 %340, label %342, label %341

341:                                              ; preds = %338, %336
  br label %342

342:                                              ; preds = %341, %338
  %343 = phi i32 [ 0, %341 ], [ %337, %338 ]
  %344 = load volatile i32, ptr %319, align 4, !tbaa !64
  %345 = icmp ne i32 %344, 2048
  %346 = icmp ne i32 %328, 0
  %347 = select i1 %346, i1 true, i1 %345
  %348 = icmp eq i32 %343, 0
  %349 = or i1 %348, %347
  br i1 %349, label %350, label %356

350:                                              ; preds = %342
  %351 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 5, ptr %351, align 8, !tbaa !69
  %352 = getelementptr inbounds nuw i8, ptr %37, i64 2073
  store volatile i8 1, ptr %352, align 1, !tbaa !70
  %353 = load volatile i32, ptr %319, align 4, !tbaa !64
  %354 = zext i32 %353 to i64
  %355 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %354, i64 noundef %329, ptr noundef nonnull @.str.36) #10
  br label %486

356:                                              ; preds = %342
  %357 = or disjoint i64 %69, 6144
  %358 = getelementptr inbounds nuw i8, ptr %154, i64 2048
  %359 = getelementptr inbounds nuw i8, ptr %154, i64 2304
  call fastcc void @format_auth_request(ptr noundef nonnull %358) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.37) #10
  %360 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %360, align 1, !tbaa !23
  %361 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 10, i64 noundef 112, ptr noundef nonnull %3) #10
  %362 = call i64 @lv1_hcall(i64 noundef 163, i64 noundef 10, i64 noundef %357, i64 noundef 112, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %363 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %364 = add i32 %363, 1
  store volatile i32 %364, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %365 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %366 = trunc i64 %362 to i32
  %367 = getelementptr inbounds nuw i8, ptr %37, i64 2084
  store volatile i32 %366, ptr %367, align 4, !tbaa !71
  %368 = trunc i64 %365 to i32
  %369 = getelementptr inbounds nuw i8, ptr %37, i64 2088
  store volatile i32 %368, ptr %369, align 8, !tbaa !72
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.38) #10
  call fastcc void @format_s32(ptr noundef %4, i32 noundef signext %366) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.39) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %368) #10
  %370 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %370, align 1, !tbaa !23
  %371 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %362, i64 noundef %365, ptr noundef nonnull %3) #10
  %372 = icmp ne i64 %362, 0
  %373 = icmp eq i64 %365, 0
  %374 = select i1 %372, i1 true, i1 %373
  br i1 %374, label %375, label %377

375:                                              ; preds = %356
  %376 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 6, ptr %376, align 8, !tbaa !69
  br label %486

377:                                              ; preds = %356
  call fastcc void @prefill_buffer(ptr noundef nonnull %359, i32 noundef zeroext 112, i8 noundef zeroext 0) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.40) #10
  %378 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %378, align 1, !tbaa !23
  %379 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 10, i64 noundef 112, ptr noundef nonnull %3) #10
  %380 = call i64 @native_clock() #9
  %381 = getelementptr inbounds nuw i8, ptr %37, i64 2092
  %382 = or disjoint i64 %69, 6400
  br label %383

383:                                              ; preds = %403, %377
  %384 = phi i32 [ 0, %377 ], [ %386, %403 ]
  %385 = phi i32 [ 0, %377 ], [ %404, %403 ]
  %386 = add i32 %384, 1
  %387 = sub nuw nsw i32 112, %385
  %388 = zext nneg i32 %385 to i64
  %389 = or disjoint i64 %388, %382
  %390 = zext nneg i32 %387 to i64
  %391 = call i64 @lv1_hcall(i64 noundef 162, i64 noundef 10, i64 noundef %389, i64 noundef %390, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %392 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %393 = add i32 %392, 1
  store volatile i32 %393, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %394 = trunc i64 %391 to i32
  store volatile i32 %394, ptr %381, align 4, !tbaa !73
  %395 = icmp eq i64 %391, 0
  br i1 %395, label %396, label %408

396:                                              ; preds = %383
  %397 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %398 = icmp eq i64 %397, 0
  br i1 %398, label %403, label %399

399:                                              ; preds = %396
  %400 = trunc i64 %397 to i32
  %401 = add i32 %385, %400
  %402 = icmp ugt i32 %401, 111
  br i1 %402, label %408, label %403

403:                                              ; preds = %399, %396
  %404 = phi i32 [ %401, %399 ], [ %385, %396 ]
  %405 = call i64 @native_clock() #9
  %406 = sub i64 %405, %380
  %407 = icmp ugt i64 %406, 159599999
  br i1 %407, label %408, label %383

408:                                              ; preds = %403, %399, %383
  %409 = phi i32 [ %385, %383 ], [ %401, %399 ], [ %404, %403 ]
  %410 = call i64 @native_clock() #9
  %411 = getelementptr inbounds nuw i8, ptr %37, i64 2096
  store volatile i32 %409, ptr %411, align 8, !tbaa !74
  %412 = getelementptr inbounds nuw i8, ptr %37, i64 2100
  store volatile i32 %386, ptr %412, align 4, !tbaa !75
  %413 = sub i64 %410, %380
  %414 = getelementptr inbounds nuw i8, ptr %37, i64 2104
  store volatile i64 %413, ptr %414, align 8, !tbaa !76
  %415 = icmp ugt i32 %409, 3
  br i1 %415, label %416, label %451

416:                                              ; preds = %408
  %417 = load volatile i8, ptr %359, align 1, !tbaa !23
  %418 = zext i8 %417 to i32
  %419 = shl nuw i32 %418, 24
  %420 = getelementptr inbounds nuw i8, ptr %154, i64 2305
  %421 = load volatile i8, ptr %420, align 1, !tbaa !23
  %422 = zext i8 %421 to i32
  %423 = shl nuw nsw i32 %422, 16
  %424 = or disjoint i32 %423, %419
  %425 = getelementptr inbounds nuw i8, ptr %154, i64 2306
  %426 = load volatile i8, ptr %425, align 1, !tbaa !23
  %427 = zext i8 %426 to i32
  %428 = shl nuw nsw i32 %427, 8
  %429 = or disjoint i32 %424, %428
  %430 = getelementptr inbounds nuw i8, ptr %154, i64 2307
  %431 = load volatile i8, ptr %430, align 1, !tbaa !23
  %432 = zext i8 %431 to i32
  %433 = or disjoint i32 %429, %432
  %434 = getelementptr inbounds nuw i8, ptr %37, i64 2080
  store volatile i32 %433, ptr %434, align 8, !tbaa !77
  %435 = icmp ugt i32 %409, 35
  br i1 %435, label %436, label %451

436:                                              ; preds = %416
  %437 = getelementptr inbounds nuw i8, ptr %154, i64 2338
  %438 = load volatile i8, ptr %437, align 1, !tbaa !23
  %439 = zext i8 %438 to i16
  %440 = shl nuw i16 %439, 8
  %441 = getelementptr inbounds nuw i8, ptr %154, i64 2339
  %442 = load volatile i8, ptr %441, align 1, !tbaa !23
  %443 = zext i8 %442 to i16
  %444 = or disjoint i16 %440, %443
  %445 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  store volatile i16 %444, ptr %445, align 2, !tbaa !78
  %446 = icmp ugt i32 %409, 56
  br i1 %446, label %447, label %451

447:                                              ; preds = %436
  %448 = getelementptr inbounds nuw i8, ptr %154, i64 2360
  %449 = load volatile i8, ptr %448, align 1, !tbaa !23
  %450 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  store volatile i8 %449, ptr %450, align 4, !tbaa !79
  br label %451

451:                                              ; preds = %447, %436, %416, %408
  switch i32 %409, label %461 [
    i32 112, label %452
    i32 0, label %462
  ]

452:                                              ; preds = %451
  %453 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  %454 = load volatile i16, ptr %453, align 2, !tbaa !78
  %455 = icmp eq i16 %454, 0
  br i1 %455, label %456, label %460

456:                                              ; preds = %452
  %457 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  %458 = load volatile i8, ptr %457, align 4, !tbaa !79
  %459 = icmp eq i8 %458, 0
  br i1 %459, label %460, label %462

460:                                              ; preds = %456, %452
  br label %462

461:                                              ; preds = %451
  br label %462

462:                                              ; preds = %461, %460, %456, %451
  %463 = phi i8 [ 1, %456 ], [ 4, %461 ], [ 2, %460 ], [ 3, %451 ]
  %464 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 %463, ptr %464, align 8, !tbaa !69
  %465 = getelementptr inbounds nuw i8, ptr %154, i64 2368
  call fastcc void @prefill_buffer(ptr noundef nonnull %465, i32 noundef zeroext 48, i8 noundef zeroext 0) #10
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.41) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %409) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.20) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %386) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.42) #10
  %466 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  %467 = load volatile i16, ptr %466, align 2, !tbaa !78
  %468 = zext i16 %467 to i32
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %468) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.43) #10
  %469 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  %470 = load volatile i8, ptr %469, align 4, !tbaa !79
  %471 = zext i8 %470 to i32
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %471) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.44) #10
  %472 = load volatile i8, ptr %464, align 8, !tbaa !69
  %473 = icmp ult i8 %472, 7
  br i1 %473, label %474, label %478

474:                                              ; preds = %462
  %475 = zext nneg i8 %472 to i64
  %476 = getelementptr inbounds nuw [8 x i8], ptr @auth_verdict_to_str.STRS, i64 %475
  %477 = load ptr, ptr %476, align 8, !tbaa !32
  br label %478

478:                                              ; preds = %474, %462
  %479 = phi ptr [ %477, %474 ], [ @.str.63, %462 ]
  call fastcc void @append_str(ptr noundef %4, ptr noundef %479) #10
  %480 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %480, align 1, !tbaa !23
  %481 = load volatile i16, ptr %466, align 2, !tbaa !78
  %482 = zext i16 %481 to i64
  %483 = load volatile i8, ptr %469, align 4, !tbaa !79
  %484 = zext i8 %483 to i64
  %485 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %482, i64 noundef %484, ptr noundef nonnull %3) #10
  br label %486

486:                                              ; preds = %478, %375, %350
  %487 = getelementptr inbounds nuw i8, ptr %37, i64 1640
  %488 = getelementptr inbounds nuw i8, ptr %37, i64 1816
  %489 = getelementptr inbounds nuw i8, ptr %37, i64 1692
  %490 = getelementptr inbounds nuw i8, ptr %37, i64 1880
  %491 = getelementptr inbounds nuw i8, ptr %37, i64 1720
  %492 = getelementptr inbounds nuw i8, ptr %37, i64 1736
  %493 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 16, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 8, i32 noundef zeroext 8, ptr noundef nonnull @.str.45, ptr noundef %152, i64 noundef %69, ptr noundef nonnull %154, i64 noundef %155, ptr noundef nonnull %37, ptr noundef nonnull %487, ptr noundef nonnull %488, ptr noundef nonnull %489, ptr noundef nonnull %490, ptr noundef nonnull %491, ptr noundef nonnull %492) #10
  %494 = icmp eq i32 %493, 1
  br i1 %494, label %562, label %495

495:                                              ; preds = %486
  %496 = getelementptr inbounds nuw i8, ptr %37, i64 1974
  br label %497

497:                                              ; preds = %509, %495
  %498 = phi i64 [ 0, %495 ], [ %513, %509 ]
  %499 = icmp eq i64 %498, 32
  br i1 %499, label %500, label %509

500:                                              ; preds = %497
  %501 = getelementptr inbounds nuw i8, ptr %37, i64 1644
  %502 = getelementptr inbounds nuw i8, ptr %37, i64 1824
  %503 = getelementptr inbounds nuw i8, ptr %37, i64 1696
  %504 = getelementptr inbounds nuw i8, ptr %37, i64 1888
  %505 = getelementptr inbounds nuw i8, ptr %37, i64 1724
  %506 = getelementptr inbounds nuw i8, ptr %37, i64 1737
  %507 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 0, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 9, i32 noundef zeroext 16, ptr noundef nonnull @.str.46, ptr noundef %152, i64 noundef %69, ptr noundef nonnull %154, i64 noundef %155, ptr noundef nonnull %37, ptr noundef nonnull %501, ptr noundef nonnull %502, ptr noundef nonnull %503, ptr noundef nonnull %504, ptr noundef nonnull %505, ptr noundef nonnull %506) #10
  %508 = icmp eq i32 %507, 1
  br i1 %508, label %562, label %514

509:                                              ; preds = %497
  %510 = getelementptr inbounds nuw i8, ptr %154, i64 %498
  %511 = load volatile i8, ptr %510, align 1, !tbaa !23
  %512 = getelementptr inbounds nuw i8, ptr %496, i64 %498
  store volatile i8 %511, ptr %512, align 1, !tbaa !23
  %513 = add nuw nsw i64 %498, 1
  br label %497, !llvm.loop !80

514:                                              ; preds = %500
  %515 = getelementptr inbounds nuw i8, ptr %37, i64 1648
  %516 = getelementptr inbounds nuw i8, ptr %37, i64 1832
  %517 = getelementptr inbounds nuw i8, ptr %37, i64 1700
  %518 = getelementptr inbounds nuw i8, ptr %37, i64 1896
  %519 = getelementptr inbounds nuw i8, ptr %37, i64 1728
  %520 = getelementptr inbounds nuw i8, ptr %37, i64 1738
  %521 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 17, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 10, i32 noundef zeroext 32, ptr noundef nonnull @.str.47, ptr noundef %152, i64 noundef %69, ptr noundef nonnull %154, i64 noundef %155, ptr noundef nonnull %37, ptr noundef nonnull %515, ptr noundef nonnull %516, ptr noundef nonnull %517, ptr noundef nonnull %518, ptr noundef nonnull %519, ptr noundef nonnull %520) #10
  %522 = icmp eq i32 %521, 1
  br i1 %522, label %562, label %523

523:                                              ; preds = %514
  %524 = getelementptr inbounds nuw i8, ptr %37, i64 1652
  %525 = getelementptr inbounds nuw i8, ptr %37, i64 1840
  %526 = getelementptr inbounds nuw i8, ptr %37, i64 1704
  %527 = getelementptr inbounds nuw i8, ptr %37, i64 1904
  %528 = getelementptr inbounds nuw i8, ptr %37, i64 1732
  %529 = getelementptr inbounds nuw i8, ptr %37, i64 1739
  %530 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 16, i32 noundef zeroext 1, i32 noundef zeroext 2048, i32 noundef zeroext 3, i32 noundef zeroext 11, i32 noundef zeroext 64, ptr noundef nonnull @.str.48, ptr noundef %152, i64 noundef %69, ptr noundef nonnull %154, i64 noundef %155, ptr noundef nonnull %37, ptr noundef nonnull %524, ptr noundef nonnull %525, ptr noundef nonnull %526, ptr noundef nonnull %527, ptr noundef nonnull %528, ptr noundef nonnull %529) #10
  %531 = icmp eq i32 %530, 1
  br i1 %531, label %562, label %532

532:                                              ; preds = %523
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.49) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %134) #10
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.50) #10
  %533 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %533, align 1, !tbaa !23
  %534 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %134, i64 noundef 1048576, ptr noundef nonnull %3) #10
  %535 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef %59, i64 noundef %134, i64 noundef 1048576, i64 noundef 0, i64 noundef 0) #9
  %536 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %537 = add i32 %536, 1
  store volatile i32 %537, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %538 = trunc i64 %535 to i32
  %539 = getelementptr inbounds nuw i8, ptr %37, i64 1616
  store volatile i32 %538, ptr %539, align 8, !tbaa !81
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.51) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %538) #10
  %540 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %540, align 1, !tbaa !23
  %541 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %535, i64 noundef 0, ptr noundef nonnull %3) #10
  br label %542

542:                                              ; preds = %532, %150
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.52) #10
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %134) #10
  %543 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %543, align 1, !tbaa !23
  %544 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %134, i64 noundef 0, ptr noundef nonnull %3) #10
  %545 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef %59, i64 noundef %134, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %546 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %547 = add i32 %546, 1
  store volatile i32 %547, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %548 = trunc i64 %545 to i32
  %549 = getelementptr inbounds nuw i8, ptr %37, i64 1620
  store volatile i32 %548, ptr %549, align 4, !tbaa !82
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.53) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %548) #10
  %550 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %550, align 1, !tbaa !23
  %551 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %545, i64 noundef 0, ptr noundef nonnull %3) #10
  br label %552

552:                                              ; preds = %542, %130
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.54) #10
  %553 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %553, align 1, !tbaa !23
  %554 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #10
  %555 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %556 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %557 = add i32 %556, 1
  store volatile i32 %557, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %558 = trunc i64 %555 to i32
  %559 = getelementptr inbounds nuw i8, ptr %37, i64 1624
  store volatile i32 %558, ptr %559, align 8, !tbaa !83
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.55) #10
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %558) #10
  %560 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %560, align 1, !tbaa !23
  %561 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %555, i64 noundef 0, ptr noundef nonnull %3) #10
  br label %562

562:                                              ; preds = %552, %523, %514, %500, %486, %298, %222, %171, %120
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.56) #10
  %563 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %564 = icmp eq i32 %563, 0
  br i1 %564, label %565, label %566

565:                                              ; preds = %562
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.57) #10
  store volatile i32 0, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %568

566:                                              ; preds = %562
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.58) #10
  %567 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %567) #10
  br label %568

568:                                              ; preds = %101, %565, %566
  %569 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %569, align 1, !tbaa !23
  %570 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %571 = zext i32 %570 to i64
  %572 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %573 = zext i32 %572 to i64
  %574 = call signext i32 @hddlog_write(i32 noundef zeroext 1162757152, i64 noundef %571, i64 noundef %573, ptr noundef nonnull %3) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #11
  %575 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %576 = or i32 %575, 2
  store volatile i32 %576, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  br label %577

577:                                              ; preds = %568, %47
  %578 = getelementptr inbounds nuw i8, ptr %37, i64 1024
  %579 = zext nneg i32 %10 to i64
  %580 = getelementptr inbounds nuw [64 x i8], ptr %578, i64 %579
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #11
  store ptr %580, ptr %2, align 8, !tbaa !32
  switch i32 %10, label %670 [
    i32 0, label %581
    i32 1, label %598
    i32 2, label %627
    i32 3, label %635
    i32 4, label %645
    i32 5, label %652
    i32 6, label %660
    i32 7, label %664
  ]

581:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.93) #10
  %582 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  %583 = load volatile i8, ptr %582, align 8, !tbaa !69
  %584 = icmp ult i8 %583, 7
  br i1 %584, label %585, label %589

585:                                              ; preds = %581
  %586 = zext nneg i8 %583 to i64
  %587 = getelementptr inbounds nuw [8 x i8], ptr @auth_verdict_to_str.STRS, i64 %586
  %588 = load ptr, ptr %587, align 8, !tbaa !32
  br label %589

589:                                              ; preds = %585, %581
  %590 = phi ptr [ %588, %585 ], [ @.str.63, %581 ]
  call fastcc void @append_str(ptr noundef %2, ptr noundef %590) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.94) #10
  %591 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  %592 = load volatile i16, ptr %591, align 2, !tbaa !78
  %593 = zext i16 %592 to i32
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %593) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.95) #10
  %594 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  %595 = load volatile i8, ptr %594, align 4, !tbaa !79
  %596 = zext i8 %595 to i32
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %596) #10
  %597 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

598:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.96) #10
  %599 = getelementptr inbounds nuw i8, ptr %37, i64 1736
  %600 = load volatile i8, ptr %599, align 8, !tbaa !84
  %601 = icmp ult i8 %600, 4
  br i1 %601, label %602, label %606

602:                                              ; preds = %598
  %603 = zext nneg i8 %600 to i64
  %604 = getelementptr inbounds nuw [8 x i8], ptr @class_to_str.STRS, i64 %603
  %605 = load ptr, ptr %604, align 8, !tbaa !32
  br label %606

606:                                              ; preds = %602, %598
  %607 = phi ptr [ %605, %602 ], [ @.str.86, %598 ]
  call fastcc void @append_str(ptr noundef %2, ptr noundef %607) #10
  %608 = load volatile i8, ptr %599, align 8, !tbaa !84
  %609 = icmp eq i8 %608, 2
  br i1 %609, label %612, label %610

610:                                              ; preds = %606
  %611 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

612:                                              ; preds = %606
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.97) #10
  %613 = getelementptr inbounds nuw i8, ptr %37, i64 1974
  %614 = load ptr, ptr %2, align 8
  br label %615

615:                                              ; preds = %619, %612
  %616 = phi i64 [ %626, %619 ], [ 1, %612 ]
  %617 = phi ptr [ %625, %619 ], [ %614, %612 ]
  %618 = icmp eq i64 %616, 6
  br i1 %618, label %672, label %619

619:                                              ; preds = %615
  %620 = getelementptr inbounds nuw i8, ptr %613, i64 %616
  %621 = load volatile i8, ptr %620, align 1, !tbaa !23
  %622 = add i8 %621, -32
  %623 = icmp ult i8 %622, 95
  %624 = select i1 %623, i8 %621, i8 46
  %625 = getelementptr inbounds nuw i8, ptr %617, i64 1
  store i8 %624, ptr %617, align 1, !tbaa !23
  %626 = add nuw nsw i64 %616, 1
  br label %615, !llvm.loop !85

627:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.98) #10
  %628 = getelementptr inbounds nuw i8, ptr %37, i64 2096
  %629 = load volatile i32, ptr %628, align 8, !tbaa !74
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %629) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.99) #10
  %630 = getelementptr inbounds nuw i8, ptr %37, i64 2100
  %631 = load volatile i32, ptr %630, align 4, !tbaa !75
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %631) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.100) #10
  %632 = getelementptr inbounds nuw i8, ptr %37, i64 2088
  %633 = load volatile i32, ptr %632, align 8, !tbaa !72
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %633) #10
  %634 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

635:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.101) #10
  %636 = getelementptr inbounds nuw i8, ptr %37, i64 2008
  %637 = load volatile i32, ptr %636, align 8, !tbaa !86
  call fastcc void @format_s32(ptr noundef %2, i32 noundef signext %637) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.102) #10
  %638 = getelementptr inbounds nuw i8, ptr %37, i64 2012
  %639 = load volatile i32, ptr %638, align 4, !tbaa !68
  call fastcc void @format_s32(ptr noundef %2, i32 noundef signext %639) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.103) #10
  %640 = getelementptr inbounds nuw i8, ptr %37, i64 2084
  %641 = load volatile i32, ptr %640, align 4, !tbaa !71
  call fastcc void @format_s32(ptr noundef %2, i32 noundef signext %641) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.104) #10
  %642 = getelementptr inbounds nuw i8, ptr %37, i64 2092
  %643 = load volatile i32, ptr %642, align 4, !tbaa !73
  call fastcc void @format_s32(ptr noundef %2, i32 noundef signext %643) #10
  %644 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

645:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.105) #10
  %646 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %646) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.106) #10
  %647 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !26
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %647) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.107) #10
  %648 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %649 = zext i16 %648 to i32
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %649) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.108) #10
  %650 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %650) #10
  %651 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

652:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.109) #10
  %653 = getelementptr inbounds nuw i8, ptr %37, i64 1720
  %654 = load volatile i32, ptr %653, align 8, !tbaa !87
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %654) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.110) #10
  %655 = getelementptr inbounds nuw i8, ptr %37, i64 1724
  %656 = load volatile i32, ptr %655, align 4, !tbaa !88
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %656) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.111) #10
  %657 = getelementptr inbounds nuw i8, ptr %37, i64 1728
  %658 = load volatile i32, ptr %657, align 8, !tbaa !89
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %658) #10
  %659 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

660:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.112) #10
  %661 = getelementptr inbounds nuw i8, ptr %37, i64 1760
  %662 = load volatile i64, ptr %661, align 8, !tbaa !42
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %662) #10
  %663 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

664:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.113) #10
  %665 = getelementptr inbounds nuw i8, ptr %37, i64 1744
  %666 = load volatile i64, ptr %665, align 8, !tbaa !49
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %666) #10
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.114) #10
  %667 = getelementptr inbounds nuw i8, ptr %37, i64 1752
  %668 = load volatile i64, ptr %667, align 8, !tbaa !51
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %668) #10
  %669 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

670:                                              ; preds = %577
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.115) #10
  %671 = load ptr, ptr %2, align 8, !tbaa !32
  br label %672

672:                                              ; preds = %615, %589, %610, %627, %635, %645, %652, %660, %664, %670
  %673 = phi ptr [ %671, %670 ], [ %669, %664 ], [ %663, %660 ], [ %659, %652 ], [ %651, %645 ], [ %644, %635 ], [ %634, %627 ], [ %597, %589 ], [ %611, %610 ], [ %617, %615 ]
  store i8 0, ptr %673, align 1, !tbaa !23
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #11
  br label %674

674:                                              ; preds = %33, %13, %672
  %675 = phi ptr [ %580, %672 ], [ inttoptr (i64 3165888 to ptr), %33 ], [ inttoptr (i64 3165888 to ptr), %13 ]
  ret ptr %675
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc ptr @get_arena() unnamed_addr #4 {
  %1 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %2 = tail call fastcc signext i32 @arena_rw(i64 noundef %1) #10
  %3 = icmp eq i32 %2, 0
  %4 = inttoptr i64 %1 to ptr
  %5 = select i1 %3, ptr null, ptr %4
  ret ptr %5
}

; Function Attrs: minsize optsize
declare i64 @native_alloc(i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc signext range(i32 0, 2) i32 @arena_rw(i64 noundef %0) unnamed_addr #4 {
  %2 = load volatile i64, ptr inttoptr (i64 9652608 to ptr), align 128, !tbaa !19
  %3 = and i64 %2, -260046849
  %4 = icmp eq i64 %3, 2147483648
  br i1 %4, label %5, label %22

5:                                                ; preds = %1
  %6 = load volatile i64, ptr inttoptr (i64 38102456 to ptr), align 8, !tbaa !19
  %7 = icmp eq i64 %6, %2
  br i1 %7, label %8, label %22

8:                                                ; preds = %5
  %9 = load volatile i64, ptr inttoptr (i64 38036872 to ptr), align 8, !tbaa !19
  %10 = or disjoint i64 %2, 131072
  %11 = icmp ne i64 %9, %10
  %12 = and i64 %0, 63
  %13 = icmp ne i64 %12, 0
  %14 = or i1 %13, %11
  %15 = icmp ult i64 %0, %10
  %16 = or i1 %15, %14
  br i1 %16, label %22, label %17

17:                                               ; preds = %8
  %18 = add i64 %0, 4096
  %19 = or disjoint i64 %2, 393216
  %20 = icmp ule i64 %18, %19
  %21 = zext i1 %20 to i32
  br label %22

22:                                               ; preds = %17, %8, %5, %1
  %23 = phi i32 [ 0, %1 ], [ %21, %17 ], [ 0, %8 ], [ 0, %5 ]
  ret i32 %23
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @append_str(ptr nofree noundef nonnull captures(none) %0, ptr nofree noundef readonly captures(none) %1) unnamed_addr #5 {
  br label %3

3:                                                ; preds = %7, %2
  %4 = phi ptr [ %1, %2 ], [ %8, %7 ]
  %5 = load i8, ptr %4, align 1, !tbaa !23
  %6 = icmp eq i8 %5, 0
  br i1 %6, label %11, label %7

7:                                                ; preds = %3
  %8 = getelementptr inbounds nuw i8, ptr %4, i64 1
  %9 = load ptr, ptr %0, align 8, !tbaa !32
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 1
  store ptr %10, ptr %0, align 8, !tbaa !32
  store i8 %5, ptr %9, align 1, !tbaa !23
  br label %3, !llvm.loop !90

11:                                               ; preds = %3
  ret void
}

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_dec(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #5 {
  %3 = alloca [12 x i8], align 1
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #11
  %4 = icmp eq i32 %1, 0
  br i1 %4, label %5, label %8

5:                                                ; preds = %2
  %6 = load ptr, ptr %0, align 8, !tbaa !32
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 1
  store ptr %7, ptr %0, align 8, !tbaa !32
  store i8 48, ptr %6, align 1, !tbaa !23
  br label %30

8:                                                ; preds = %2, %12
  %9 = phi i64 [ %19, %12 ], [ 0, %2 ]
  %10 = phi i32 [ %14, %12 ], [ %1, %2 ]
  %11 = icmp eq i32 %10, 0
  br i1 %11, label %21, label %12

12:                                               ; preds = %8
  %13 = freeze i32 %10
  %14 = udiv i32 %13, 10
  %15 = mul i32 %14, 10
  %16 = sub i32 %13, %15
  %17 = trunc nuw nsw i32 %16 to i8
  %18 = or disjoint i8 %17, 48
  %19 = add nuw nsw i64 %9, 1
  %20 = getelementptr inbounds nuw i8, ptr %3, i64 %9
  store i8 %18, ptr %20, align 1, !tbaa !23
  br label %8, !llvm.loop !91

21:                                               ; preds = %8, %24
  %22 = phi i64 [ %25, %24 ], [ %9, %8 ]
  %23 = icmp sgt i64 %22, 0
  br i1 %23, label %24, label %30

24:                                               ; preds = %21
  %25 = add nsw i64 %22, -1
  %26 = getelementptr inbounds nuw i8, ptr %3, i64 %25
  %27 = load i8, ptr %26, align 1, !tbaa !23
  %28 = load ptr, ptr %0, align 8, !tbaa !32
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 1
  store ptr %29, ptr %0, align 8, !tbaa !32
  store i8 %27, ptr %28, align 1, !tbaa !23
  br label %21, !llvm.loop !92

30:                                               ; preds = %21, %5
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #11
  ret void
}

; Function Attrs: minsize optsize
declare i64 @lv1_hcall(i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex64(ptr nofree noundef nonnull captures(none) %0, i64 noundef %1) unnamed_addr #5 {
  tail call fastcc void @format_hex_n(ptr noundef %0, i64 noundef %1, i32 noundef signext 16) #10
  ret void
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @setup_atapi_block(ptr nofree noundef captures(address) %0, i8 noundef zeroext range(i8 0, 38) %1, i32 noundef zeroext range(i32 0, 37) %2, i32 noundef zeroext range(i32 0, 2) %3, i32 noundef zeroext range(i32 0, 2) %4, i64 noundef %5) unnamed_addr #6 {
  tail call fastcc void @prefill_buffer(ptr noundef %0, i32 noundef zeroext 64, i8 noundef zeroext 0) #10
  store volatile i8 %1, ptr %0, align 1, !tbaa !23
  switch i8 %1, label %10 [
    i8 18, label %7
    i8 3, label %7
  ]

7:                                                ; preds = %6, %6
  %8 = trunc nuw nsw i32 %2 to i8
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 4
  store volatile i8 %8, ptr %9, align 1, !tbaa !23
  br label %10

10:                                               ; preds = %7, %6
  %11 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store volatile i32 12, ptr %11, align 4, !tbaa !20
  %12 = getelementptr inbounds nuw i8, ptr %0, i64 36
  store volatile i32 %2, ptr %12, align 4, !tbaa !20
  %13 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store volatile i32 1, ptr %13, align 4, !tbaa !20
  %14 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store volatile i32 %3, ptr %14, align 4, !tbaa !20
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store volatile i32 %4, ptr %15, align 4, !tbaa !20
  %16 = getelementptr inbounds nuw i8, ptr %0, i64 56
  store volatile i64 %5, ptr %16, align 8, !tbaa !19
  ret void
}

; Function Attrs: minsize nounwind optsize
define internal fastcc signext range(i32 0, 2) i32 @poll_completion(i64 noundef range(i64 0, 8) %0, i64 noundef %1, ptr nofree noundef captures(address) %2, ptr nofree noundef captures(address) %3, ptr nofree noundef captures(address) %4) unnamed_addr #0 {
  %6 = tail call i64 @native_clock() #9
  br label %7

7:                                                ; preds = %19, %5
  %8 = phi i32 [ 0, %5 ], [ %20, %19 ]
  %9 = icmp eq i32 %8, 200000
  br i1 %9, label %24, label %10

10:                                               ; preds = %7
  %11 = tail call i64 @lv1_hcall(i64 noundef 254, i64 noundef %0, i64 noundef %1, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %12 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %13 = add i32 %12, 1
  store volatile i32 %13, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %14 = icmp eq i64 %11, 0
  br i1 %14, label %21, label %15

15:                                               ; preds = %10
  %16 = tail call i64 @native_clock() #9
  %17 = sub i64 %16, %6
  %18 = icmp ugt i64 %17, 159999999
  br i1 %18, label %24, label %19

19:                                               ; preds = %15
  %20 = add nuw nsw i32 %8, 1
  br label %7, !llvm.loop !93

21:                                               ; preds = %10
  %22 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  store volatile i64 %22, ptr %2, align 8, !tbaa !19
  %23 = add nuw nsw i32 %8, 1
  store volatile i32 %23, ptr %3, align 4, !tbaa !20
  br label %24

24:                                               ; preds = %7, %15, %21
  %25 = phi i32 [ 0, %21 ], [ 1, %15 ], [ 1, %7 ]
  %26 = tail call i64 @native_clock() #9
  %27 = sub i64 %26, %6
  store volatile i64 %27, ptr %4, align 8, !tbaa !19
  ret i32 %25
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @prefill_buffer(ptr nofree noundef captures(address) %0, i32 noundef zeroext range(i32 8, 2049) %1, i8 noundef zeroext range(i8 -91, 1) %2) unnamed_addr #6 {
  %4 = zext nneg i32 %1 to i64
  br label %5

5:                                                ; preds = %9, %3
  %6 = phi i64 [ %11, %9 ], [ 0, %3 ]
  %7 = icmp eq i64 %6, %4
  br i1 %7, label %8, label %9

8:                                                ; preds = %5
  ret void

9:                                                ; preds = %5
  %10 = getelementptr inbounds nuw i8, ptr %0, i64 %6
  store volatile i8 %2, ptr %10, align 1, !tbaa !23
  %11 = add nuw nsw i64 %6, 1
  br label %5, !llvm.loop !94
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @format_ascii(ptr nofree noundef nonnull captures(none) %0, ptr nofree noundef captures(address) %1, i32 noundef zeroext range(i32 8, 17) %2) unnamed_addr #7 {
  %4 = zext nneg i32 %2 to i64
  br label %5

5:                                                ; preds = %9, %3
  %6 = phi i64 [ %17, %9 ], [ 0, %3 ]
  %7 = icmp eq i64 %6, %4
  br i1 %7, label %8, label %9

8:                                                ; preds = %5
  ret void

9:                                                ; preds = %5
  %10 = getelementptr inbounds nuw i8, ptr %1, i64 %6
  %11 = load volatile i8, ptr %10, align 1, !tbaa !23
  %12 = add i8 %11, -32
  %13 = icmp ult i8 %12, 95
  %14 = load ptr, ptr %0, align 8, !tbaa !32
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 1
  store ptr %15, ptr %0, align 8, !tbaa !32
  %16 = select i1 %13, i8 %11, i8 46
  store i8 %16, ptr %14, align 1, !tbaa !23
  %17 = add nuw nsw i64 %6, 1
  br label %5, !llvm.loop !95
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex32(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #5 {
  %3 = zext i32 %1 to i64
  tail call fastcc void @format_hex_n(ptr noundef %0, i64 noundef %3, i32 noundef signext 8) #10
  ret void
}

; Function Attrs: minsize nounwind optsize
define internal fastcc void @query_vuart_param(i64 noundef range(i64 2, 11) %0, i64 noundef range(i64 0, 4) %1, ptr nofree noundef captures(address) %2, ptr nofree noundef captures(address) %3, ptr nofree noundef readonly captures(none) %4) unnamed_addr #0 {
  %6 = alloca [64 x i8], align 1
  %7 = alloca ptr, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #11
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #11
  store ptr %6, ptr %7, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.59) #10
  call fastcc void @append_str(ptr noundef %7, ptr noundef %4) #10
  %8 = load ptr, ptr %7, align 8, !tbaa !32
  store i8 0, ptr %8, align 1, !tbaa !23
  %9 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %0, i64 noundef %1, ptr noundef nonnull %6) #10
  %10 = call i64 @lv1_hcall(i64 noundef 165, i64 noundef %0, i64 noundef %1, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #9
  %11 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %12 = add i32 %11, 1
  store volatile i32 %12, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %13 = trunc i64 %10 to i32
  store volatile i32 %13, ptr %2, align 4, !tbaa !20
  %14 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  store volatile i64 %14, ptr %3, align 8, !tbaa !19
  store ptr %6, ptr %7, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.60) #10
  call fastcc void @append_str(ptr noundef %7, ptr noundef %4) #10
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.61) #10
  call fastcc void @format_s32(ptr noundef %7, i32 noundef signext %13) #10
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.62) #10
  %15 = load volatile i64, ptr %3, align 8, !tbaa !19
  call fastcc void @format_hex64(ptr noundef %7, i64 noundef %15) #10
  %16 = load ptr, ptr %7, align 8, !tbaa !32
  store i8 0, ptr %16, align 1, !tbaa !23
  %17 = load volatile i64, ptr %3, align 8, !tbaa !19
  %18 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %10, i64 noundef %17, ptr noundef nonnull %6) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #11
  ret void
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @format_auth_request(ptr nofree noundef captures(address) %0) unnamed_addr #6 {
  tail call fastcc void @prefill_buffer(ptr noundef %0, i32 noundef zeroext 112, i8 noundef zeroext 0) #10
  store volatile i32 64206, ptr %0, align 4, !tbaa !20
  %2 = getelementptr inbounds nuw i8, ptr %0, i64 4
  store volatile i32 20480, ptr %2, align 4, !tbaa !20
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  store volatile i32 96, ptr %3, align 4, !tbaa !20
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 12
  store volatile i32 96, ptr %4, align 4, !tbaa !20
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 16
  store volatile i64 20485, ptr %5, align 8, !tbaa !19
  %6 = getelementptr inbounds nuw i8, ptr %0, i64 24
  store volatile i64 20480, ptr %6, align 8, !tbaa !19
  %7 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store volatile i64 1161928721058234369, ptr %7, align 8, !tbaa !19
  %8 = getelementptr inbounds nuw i8, ptr %0, i64 56
  store volatile i8 0, ptr %8, align 8, !tbaa !23
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 57
  store volatile i8 19, ptr %9, align 1, !tbaa !23
  %10 = getelementptr inbounds nuw i8, ptr %0, i64 64
  store volatile i32 75, ptr %10, align 8, !tbaa !20
  ret void
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_s32(ptr nofree noundef nonnull captures(none) %0, i32 noundef signext %1) unnamed_addr #5 {
  %3 = icmp slt i32 %1, 0
  br i1 %3, label %4, label %8

4:                                                ; preds = %2
  %5 = load ptr, ptr %0, align 8, !tbaa !32
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 1
  store ptr %6, ptr %0, align 8, !tbaa !32
  store i8 45, ptr %5, align 1, !tbaa !23
  %7 = sub nsw i32 0, %1
  br label %8

8:                                                ; preds = %2, %4
  %9 = phi i32 [ %7, %4 ], [ %1, %2 ]
  tail call fastcc void @format_dec(ptr noundef %0, i32 noundef zeroext %9) #10
  ret void
}

; Function Attrs: minsize noinline nounwind optsize
define internal fastcc signext range(i32 -1, 2) i32 @execute_read_test(i64 noundef range(i64 0, 8) %0, i32 noundef zeroext range(i32 0, 18) %1, i32 noundef zeroext range(i32 1, 2049) %2, i32 noundef zeroext range(i32 1, 2049) %3, i32 noundef zeroext range(i32 1, 4) %4, i32 noundef zeroext range(i32 8, 12) %5, i32 noundef zeroext range(i32 8, 65) %6, ptr nofree noundef readonly captures(none) %7, ptr nofree noundef captures(address) %8, i64 noundef %9, ptr nofree noundef captures(address) %10, i64 noundef %11, ptr nofree noundef captures(address) %12, ptr nofree noundef captures(address) %13, ptr nofree noundef captures(address) %14, ptr nofree noundef captures(address) %15, ptr nofree noundef captures(address) %16, ptr nofree noundef captures(address) %17, ptr nofree noundef captures(address) %18) unnamed_addr #8 {
  %20 = alloca [256 x i8], align 1
  %21 = alloca ptr, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %20) #11
  call void @llvm.lifetime.start.p0(ptr nonnull %21) #11
  tail call fastcc void @prefill_buffer(ptr noundef %10, i32 noundef zeroext 2048, i8 noundef zeroext -91) #10
  tail call fastcc void @prefill_buffer(ptr noundef %8, i32 noundef zeroext 64, i8 noundef zeroext 0) #10
  store volatile i8 40, ptr %8, align 1, !tbaa !23
  %22 = getelementptr inbounds nuw i8, ptr %8, i64 2
  store volatile i8 0, ptr %22, align 1, !tbaa !23
  %23 = getelementptr inbounds nuw i8, ptr %8, i64 3
  store volatile i8 0, ptr %23, align 1, !tbaa !23
  %24 = getelementptr inbounds nuw i8, ptr %8, i64 4
  store volatile i8 0, ptr %24, align 1, !tbaa !23
  %25 = trunc nuw nsw i32 %1 to i8
  %26 = getelementptr inbounds nuw i8, ptr %8, i64 5
  store volatile i8 %25, ptr %26, align 1, !tbaa !23
  %27 = getelementptr inbounds nuw i8, ptr %8, i64 8
  store volatile i8 1, ptr %27, align 1, !tbaa !23
  %28 = getelementptr inbounds nuw i8, ptr %8, i64 32
  store volatile i32 12, ptr %28, align 4, !tbaa !20
  %29 = getelementptr inbounds nuw i8, ptr %8, i64 36
  store volatile i32 %2, ptr %29, align 4, !tbaa !20
  %30 = getelementptr inbounds nuw i8, ptr %8, i64 40
  store volatile i32 %3, ptr %30, align 4, !tbaa !20
  %31 = getelementptr inbounds nuw i8, ptr %8, i64 44
  store volatile i32 %4, ptr %31, align 4, !tbaa !20
  %32 = getelementptr inbounds nuw i8, ptr %8, i64 48
  store volatile i32 1, ptr %32, align 4, !tbaa !20
  %33 = getelementptr inbounds nuw i8, ptr %8, i64 56
  store volatile i64 %11, ptr %33, align 8, !tbaa !19
  store ptr %20, ptr %21, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.70) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.71) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %1) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.72) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %4) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.73) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %2) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.74) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %3) #10
  %34 = load ptr, ptr %21, align 8, !tbaa !32
  store i8 0, ptr %34, align 1, !tbaa !23
  %35 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %9, i64 noundef %11, ptr noundef nonnull %20) #10
  %36 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %0, i64 noundef 1, i64 noundef %9, i64 noundef 64, i64 noundef %11, i64 noundef 2048) #9
  %37 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %38 = add i32 %37, 1
  store volatile i32 %38, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %39 = trunc i64 %36 to i32
  store volatile i32 %39, ptr %13, align 4, !tbaa !20
  %40 = icmp eq i64 %36, 0
  br i1 %40, label %41, label %53

41:                                               ; preds = %19
  %42 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %43 = call fastcc signext i32 @poll_completion(i64 noundef %0, i64 noundef %42, ptr noundef %14, ptr noundef %15, ptr noundef %16) #10
  %44 = icmp eq i32 %43, 0
  br i1 %44, label %61, label %45

45:                                               ; preds = %41
  %46 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  %47 = or i32 %46, %6
  store volatile i32 %47, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store ptr %20, ptr %21, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.75) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.76) #10
  %48 = load ptr, ptr %21, align 8, !tbaa !32
  store i8 0, ptr %48, align 1, !tbaa !23
  %49 = load volatile i32, ptr %15, align 4, !tbaa !20
  %50 = zext i32 %49 to i64
  %51 = load volatile i64, ptr %16, align 8, !tbaa !19
  %52 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %50, i64 noundef %51, ptr noundef nonnull %20) #10
  br label %127

53:                                               ; preds = %19
  %54 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %55 = icmp eq i32 %54, 0
  br i1 %55, label %56, label %57

56:                                               ; preds = %53
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  br label %57

57:                                               ; preds = %56, %53
  %58 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  %59 = icmp eq i32 %58, 0
  br i1 %59, label %60, label %61

60:                                               ; preds = %57
  store volatile i32 %39, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %61

61:                                               ; preds = %41, %57, %60
  br label %62

62:                                               ; preds = %61, %66
  %63 = phi i64 [ %72, %66 ], [ 0, %61 ]
  %64 = phi i32 [ %71, %66 ], [ 0, %61 ]
  %65 = icmp eq i64 %63, 2048
  br i1 %65, label %73, label %66

66:                                               ; preds = %62
  %67 = getelementptr inbounds nuw i8, ptr %10, i64 %63
  %68 = load volatile i8, ptr %67, align 1, !tbaa !23
  %69 = icmp eq i8 %68, -91
  %70 = zext i1 %69 to i32
  %71 = add i32 %64, %70
  %72 = add nuw nsw i64 %63, 1
  br label %62, !llvm.loop !96

73:                                               ; preds = %62
  store volatile i32 %64, ptr %17, align 4, !tbaa !20
  %74 = icmp eq i32 %64, 2048
  br i1 %74, label %110, label %75

75:                                               ; preds = %73
  %76 = getelementptr inbounds nuw i8, ptr %10, i64 1
  %77 = load volatile i8, ptr %76, align 1, !tbaa !23
  %78 = icmp eq i8 %77, 67
  br i1 %78, label %79, label %95

79:                                               ; preds = %75
  %80 = getelementptr inbounds nuw i8, ptr %10, i64 2
  %81 = load volatile i8, ptr %80, align 1, !tbaa !23
  %82 = icmp eq i8 %81, 68
  br i1 %82, label %83, label %95

83:                                               ; preds = %79
  %84 = getelementptr inbounds nuw i8, ptr %10, i64 3
  %85 = load volatile i8, ptr %84, align 1, !tbaa !23
  %86 = icmp eq i8 %85, 48
  br i1 %86, label %87, label %95

87:                                               ; preds = %83
  %88 = getelementptr inbounds nuw i8, ptr %10, i64 4
  %89 = load volatile i8, ptr %88, align 1, !tbaa !23
  %90 = icmp eq i8 %89, 48
  br i1 %90, label %91, label %95

91:                                               ; preds = %87
  %92 = getelementptr inbounds nuw i8, ptr %10, i64 5
  %93 = load volatile i8, ptr %92, align 1, !tbaa !23
  %94 = icmp eq i8 %93, 49
  br i1 %94, label %110, label %95

95:                                               ; preds = %91, %87, %83, %79, %75
  br label %96

96:                                               ; preds = %95, %103
  %97 = phi i64 [ %109, %103 ], [ 0, %95 ]
  %98 = phi i32 [ %108, %103 ], [ 0, %95 ]
  %99 = icmp eq i64 %97, 2048
  br i1 %99, label %100, label %103

100:                                              ; preds = %96
  %101 = icmp eq i32 %98, 2048
  %102 = select i1 %101, i8 1, i8 3
  br label %110

103:                                              ; preds = %96
  %104 = getelementptr inbounds nuw i8, ptr %10, i64 %97
  %105 = load volatile i8, ptr %104, align 1, !tbaa !23
  %106 = icmp eq i8 %105, 0
  %107 = zext i1 %106 to i32
  %108 = add i32 %98, %107
  %109 = add nuw nsw i64 %97, 1
  br label %96, !llvm.loop !97

110:                                              ; preds = %73, %91, %100
  %111 = phi i8 [ %102, %100 ], [ 0, %73 ], [ 2, %91 ]
  store volatile i8 %111, ptr %18, align 1, !tbaa !23
  store ptr %20, ptr %21, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.77) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.61) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %39) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.19) #10
  %112 = load volatile i64, ptr %14, align 8, !tbaa !19
  call fastcc void @format_hex64(ptr noundef %21, i64 noundef %112) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.78) #10
  %113 = zext nneg i8 %111 to i64
  %114 = getelementptr inbounds nuw [8 x i8], ptr @class_to_str.STRS, i64 %113
  %115 = load ptr, ptr %114, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %21, ptr noundef %115) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.79) #10
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %64) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.20) #10
  %116 = load volatile i32, ptr %15, align 4, !tbaa !20
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %116) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.80) #10
  call fastcc void @format_bytes_hex(ptr noundef %21, ptr noundef %10) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.81) #10
  %117 = getelementptr inbounds nuw i8, ptr %10, i64 16
  call fastcc void @format_bytes_hex(ptr noundef %21, ptr noundef nonnull %117) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.82) #10
  %118 = getelementptr inbounds nuw i8, ptr %10, i64 40
  call fastcc void @format_ascii(ptr noundef %21, ptr noundef nonnull %118, i32 noundef zeroext 8) #10
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.27) #10
  %119 = load ptr, ptr %21, align 8, !tbaa !32
  store i8 0, ptr %119, align 1, !tbaa !23
  %120 = load volatile i64, ptr %14, align 8, !tbaa !19
  %121 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %36, i64 noundef %120, ptr noundef nonnull %20) #10
  br i1 %40, label %122, label %126

122:                                              ; preds = %110
  %123 = load volatile i64, ptr %14, align 8, !tbaa !19
  %124 = and i64 %123, 255
  %125 = icmp eq i64 %124, 2
  br i1 %125, label %126, label %127

126:                                              ; preds = %122, %110
  call fastcc void @do_request_sense(i64 noundef %0, ptr noundef nonnull %8, i64 noundef %9, ptr noundef nonnull %10, i64 noundef %11, ptr noundef %12) #10
  br label %127

127:                                              ; preds = %45, %126, %122
  %128 = phi i32 [ 1, %45 ], [ -1, %126 ], [ 0, %122 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %21) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %20) #11
  ret i32 %128
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex_n(ptr nofree noundef nonnull captures(none) %0, i64 noundef %1, i32 noundef signext range(i32 8, 17) %2) unnamed_addr #5 {
  %4 = shl nuw nsw i32 %2, 2
  %5 = zext nneg i32 %4 to i64
  br label %6

6:                                                ; preds = %10, %3
  %7 = phi i64 [ %11, %10 ], [ %5, %3 ]
  %8 = icmp sgt i64 %7, 3
  br i1 %8, label %10, label %9

9:                                                ; preds = %6
  ret void

10:                                               ; preds = %6
  %11 = add nsw i64 %7, -4
  %12 = lshr i64 %1, %11
  %13 = and i64 %12, 15
  %14 = getelementptr inbounds nuw i8, ptr @HEX_DIGITS, i64 %13
  %15 = load i8, ptr %14, align 1, !tbaa !23
  %16 = load ptr, ptr %0, align 8, !tbaa !32
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 1
  store ptr %17, ptr %0, align 8, !tbaa !32
  store i8 %15, ptr %16, align 1, !tbaa !23
  br label %6, !llvm.loop !98
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @format_bytes_hex(ptr nofree noundef nonnull captures(none) %0, ptr nofree noundef captures(address) %1) unnamed_addr #7 {
  br label %3

3:                                                ; preds = %7, %2
  %4 = phi i64 [ %23, %7 ], [ 0, %2 ]
  %5 = icmp eq i64 %4, 16
  br i1 %5, label %6, label %7

6:                                                ; preds = %3
  ret void

7:                                                ; preds = %3
  %8 = getelementptr inbounds nuw i8, ptr %1, i64 %4
  %9 = load volatile i8, ptr %8, align 1, !tbaa !23
  %10 = lshr i8 %9, 4
  %11 = zext nneg i8 %10 to i64
  %12 = getelementptr inbounds nuw i8, ptr @HEX_DIGITS, i64 %11
  %13 = load i8, ptr %12, align 1, !tbaa !23
  %14 = load ptr, ptr %0, align 8, !tbaa !32
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 1
  store ptr %15, ptr %0, align 8, !tbaa !32
  store i8 %13, ptr %14, align 1, !tbaa !23
  %16 = load volatile i8, ptr %8, align 1, !tbaa !23
  %17 = and i8 %16, 15
  %18 = zext nneg i8 %17 to i64
  %19 = getelementptr inbounds nuw i8, ptr @HEX_DIGITS, i64 %18
  %20 = load i8, ptr %19, align 1, !tbaa !23
  %21 = load ptr, ptr %0, align 8, !tbaa !32
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 1
  store ptr %22, ptr %0, align 8, !tbaa !32
  store i8 %20, ptr %21, align 1, !tbaa !23
  %23 = add nuw nsw i64 %4, 1
  br label %3, !llvm.loop !99
}

; Function Attrs: minsize noinline nounwind optsize
define internal fastcc void @do_request_sense(i64 noundef range(i64 0, 8) %0, ptr nofree noundef captures(address) %1, i64 noundef %2, ptr nofree noundef captures(address) %3, i64 noundef %4, ptr nofree noundef captures(address) %5) unnamed_addr #8 {
  %7 = alloca [128 x i8], align 1
  %8 = alloca ptr, align 8
  tail call fastcc void @setup_atapi_block(ptr noundef %1, i8 noundef zeroext 3, i32 noundef zeroext 18, i32 noundef zeroext 1, i32 noundef zeroext 1, i64 noundef %4) #10
  tail call fastcc void @prefill_buffer(ptr noundef %3, i32 noundef zeroext 18, i8 noundef zeroext 0) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #11
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #11
  store ptr %7, ptr %8, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.87) #10
  call fastcc void @format_hex64(ptr noundef %8, i64 noundef %2) #10
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.23) #10
  call fastcc void @format_hex64(ptr noundef %8, i64 noundef %4) #10
  %9 = load ptr, ptr %8, align 8, !tbaa !32
  store i8 0, ptr %9, align 1, !tbaa !23
  %10 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %2, i64 noundef %4, ptr noundef nonnull %7) #10
  %11 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %0, i64 noundef 1, i64 noundef %2, i64 noundef 64, i64 noundef %4, i64 noundef 18) #9
  %12 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %13 = add i32 %12, 1
  store volatile i32 %13, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %14 = trunc i64 %11 to i32
  %15 = getelementptr inbounds nuw i8, ptr %5, i64 1656
  store volatile i32 %14, ptr %15, align 8, !tbaa !100
  %16 = icmp eq i64 %11, 0
  br i1 %16, label %17, label %42

17:                                               ; preds = %6
  %18 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !48
  %19 = getelementptr inbounds nuw i8, ptr %5, i64 1848
  %20 = getelementptr inbounds nuw i8, ptr %5, i64 1708
  %21 = getelementptr inbounds nuw i8, ptr %5, i64 1912
  %22 = call fastcc signext i32 @poll_completion(i64 noundef %0, i64 noundef %18, ptr noundef nonnull %19, ptr noundef nonnull %20, ptr noundef nonnull %21) #10
  %23 = icmp eq i32 %22, 0
  br i1 %23, label %24, label %26

24:                                               ; preds = %17
  %25 = getelementptr inbounds nuw i8, ptr %5, i64 1956
  br label %34

26:                                               ; preds = %17
  %27 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  %28 = or i32 %27, 128
  store volatile i32 %28, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !53
  store ptr %7, ptr %8, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.88) #10
  %29 = load ptr, ptr %8, align 8, !tbaa !32
  store i8 0, ptr %29, align 1, !tbaa !23
  %30 = load volatile i32, ptr %20, align 4, !tbaa !101
  %31 = zext i32 %30 to i64
  %32 = load volatile i64, ptr %21, align 8, !tbaa !102
  %33 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %31, i64 noundef %32, ptr noundef nonnull %7) #10
  br label %58

34:                                               ; preds = %24, %37
  %35 = phi i64 [ 0, %24 ], [ %41, %37 ]
  %36 = icmp eq i64 %35, 18
  br i1 %36, label %42, label %37

37:                                               ; preds = %34
  %38 = getelementptr inbounds nuw i8, ptr %3, i64 %35
  %39 = load volatile i8, ptr %38, align 1, !tbaa !23
  %40 = getelementptr inbounds nuw i8, ptr %25, i64 %35
  store volatile i8 %39, ptr %40, align 1, !tbaa !23
  %41 = add nuw nsw i64 %35, 1
  br label %34, !llvm.loop !103

42:                                               ; preds = %34, %6
  store ptr %7, ptr %8, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.89) #10
  call fastcc void @format_dec(ptr noundef %8, i32 noundef zeroext %14) #10
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.19) #10
  %43 = getelementptr inbounds nuw i8, ptr %5, i64 1848
  %44 = load volatile i64, ptr %43, align 8, !tbaa !104
  call fastcc void @format_hex64(ptr noundef %8, i64 noundef %44) #10
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.90) #10
  %45 = getelementptr inbounds nuw i8, ptr %5, i64 1958
  %46 = load volatile i8, ptr %45, align 2, !tbaa !23
  %47 = and i8 %46, 15
  %48 = zext nneg i8 %47 to i32
  call fastcc void @format_hex32(ptr noundef %8, i32 noundef zeroext %48) #10
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.91) #10
  %49 = getelementptr inbounds nuw i8, ptr %5, i64 1968
  %50 = load volatile i8, ptr %49, align 8, !tbaa !23
  %51 = zext i8 %50 to i32
  call fastcc void @format_hex32(ptr noundef %8, i32 noundef zeroext %51) #10
  call fastcc void @append_str(ptr noundef %8, ptr noundef nonnull @.str.92) #10
  %52 = getelementptr inbounds nuw i8, ptr %5, i64 1969
  %53 = load volatile i8, ptr %52, align 1, !tbaa !23
  %54 = zext i8 %53 to i32
  call fastcc void @format_hex32(ptr noundef %8, i32 noundef zeroext %54) #10
  %55 = load ptr, ptr %8, align 8, !tbaa !32
  store i8 0, ptr %55, align 1, !tbaa !23
  %56 = load volatile i64, ptr %43, align 8, !tbaa !104
  %57 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %11, i64 noundef %56, ptr noundef nonnull %7) #10
  br label %58

58:                                               ; preds = %26, %42
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #11
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #11
  ret void
}

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #3 = { minsize nofree norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #4 = { minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #5 = { minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #6 = { minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #7 = { minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #8 = { minsize noinline nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #9 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #10 = { minsize nobuiltin optsize "no-builtins" }
attributes #11 = { nounwind }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}
!llvm.errno.tbaa = !{!3}

!0 = !{i32 8, !"PIC Level", i32 2}
!1 = !{i32 7, !"PIE Level", i32 2}
!2 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!3 = !{!4, !5, i64 0}
!4 = !{!"__libc_errno", !5, i64 0}
!5 = !{!"int", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C/C++ TBAA"}
!8 = !{!9, !10, i64 24}
!9 = !{!"ProbeMailbox", !5, i64 0, !5, i64 4, !5, i64 8, !5, i64 12, !5, i64 16, !5, i64 20, !10, i64 24, !6, i64 32, !6, i64 33, !6, i64 34, !6, i64 35, !6, i64 36, !6, i64 37, !6, i64 38, !6, i64 39, !5, i64 40, !5, i64 44, !10, i64 48, !10, i64 56, !10, i64 64, !5, i64 72, !11, i64 76, !6, i64 78, !6, i64 79, !10, i64 80, !10, i64 88}
!10 = !{!"long long", !6, i64 0}
!11 = !{!"short", !6, i64 0}
!12 = !{!13, !5, i64 1668}
!13 = !{!"ProbeArena", !6, i64 0, !6, i64 512, !6, i64 1024, !5, i64 1600, !5, i64 1604, !5, i64 1608, !5, i64 1612, !5, i64 1616, !5, i64 1620, !5, i64 1624, !5, i64 1628, !5, i64 1632, !5, i64 1636, !5, i64 1640, !5, i64 1644, !5, i64 1648, !5, i64 1652, !5, i64 1656, !5, i64 1660, !5, i64 1664, !5, i64 1668, !5, i64 1672, !5, i64 1676, !5, i64 1680, !5, i64 1684, !5, i64 1688, !5, i64 1692, !5, i64 1696, !5, i64 1700, !5, i64 1704, !5, i64 1708, !5, i64 1712, !5, i64 1716, !5, i64 1720, !5, i64 1724, !5, i64 1728, !5, i64 1732, !6, i64 1736, !6, i64 1737, !6, i64 1738, !6, i64 1739, !10, i64 1744, !10, i64 1752, !10, i64 1760, !10, i64 1768, !10, i64 1776, !10, i64 1784, !10, i64 1792, !10, i64 1800, !10, i64 1808, !10, i64 1816, !10, i64 1824, !10, i64 1832, !10, i64 1840, !10, i64 1848, !10, i64 1856, !10, i64 1864, !10, i64 1872, !10, i64 1880, !10, i64 1888, !10, i64 1896, !10, i64 1904, !10, i64 1912, !6, i64 1920, !6, i64 1956, !6, i64 1974, !5, i64 2008, !5, i64 2012, !5, i64 2016, !5, i64 2020, !5, i64 2024, !10, i64 2032, !10, i64 2040, !10, i64 2048, !10, i64 2056, !10, i64 2064, !6, i64 2072, !6, i64 2073, !11, i64 2074, !6, i64 2076, !6, i64 2077, !5, i64 2080, !5, i64 2084, !5, i64 2088, !5, i64 2092, !5, i64 2096, !5, i64 2100, !10, i64 2104}
!14 = !{!13, !10, i64 1784}
!15 = !{!13, !5, i64 1672}
!16 = !{!13, !5, i64 1676}
!17 = !{!9, !6, i64 78}
!18 = !{!9, !11, i64 76}
!19 = !{!10, !10, i64 0}
!20 = !{!5, !5, i64 0}
!21 = distinct !{!21, !22}
!22 = !{!"llvm.loop.mustprogress"}
!23 = !{!6, !6, i64 0}
!24 = distinct !{!24, !22}
!25 = distinct !{!25, !22}
!26 = !{!9, !5, i64 72}
!27 = !{!9, !6, i64 79}
!28 = !{!9, !5, i64 0}
!29 = distinct !{!29, !22}
!30 = !{!9, !10, i64 64}
!31 = !{!9, !5, i64 20}
!32 = !{!33, !33, i64 0}
!33 = !{!"p1 omnipotent char", !34, i64 0}
!34 = !{!"any pointer", !6, i64 0}
!35 = !{!13, !5, i64 1664}
!36 = !{!9, !5, i64 40}
!37 = !{!9, !5, i64 44}
!38 = !{!13, !5, i64 1660}
!39 = distinct !{!39, !22}
!40 = !{!9, !5, i64 12}
!41 = !{!9, !5, i64 16}
!42 = !{!13, !10, i64 1760}
!43 = !{!13, !10, i64 1768}
!44 = !{!13, !10, i64 1776}
!45 = !{!9, !5, i64 4}
!46 = !{!13, !5, i64 1604}
!47 = !{!13, !5, i64 1608}
!48 = !{!9, !10, i64 80}
!49 = !{!13, !10, i64 1744}
!50 = !{!13, !5, i64 1612}
!51 = !{!13, !10, i64 1752}
!52 = !{!13, !5, i64 1628}
!53 = !{!9, !5, i64 8}
!54 = !{!13, !5, i64 1680}
!55 = !{!13, !10, i64 1856}
!56 = !{!13, !10, i64 1792}
!57 = !{!13, !5, i64 1632}
!58 = distinct !{!58, !22}
!59 = !{!13, !5, i64 1684}
!60 = !{!13, !10, i64 1864}
!61 = !{!13, !10, i64 1800}
!62 = !{!13, !5, i64 1636}
!63 = !{!13, !5, i64 1712}
!64 = !{!13, !5, i64 1716}
!65 = !{!13, !5, i64 1688}
!66 = !{!13, !10, i64 1872}
!67 = !{!13, !10, i64 1808}
!68 = !{!13, !5, i64 2012}
!69 = !{!13, !6, i64 2072}
!70 = !{!13, !6, i64 2073}
!71 = !{!13, !5, i64 2084}
!72 = !{!13, !5, i64 2088}
!73 = !{!13, !5, i64 2092}
!74 = !{!13, !5, i64 2096}
!75 = !{!13, !5, i64 2100}
!76 = !{!13, !10, i64 2104}
!77 = !{!13, !5, i64 2080}
!78 = !{!13, !11, i64 2074}
!79 = !{!13, !6, i64 2076}
!80 = distinct !{!80, !22}
!81 = !{!13, !5, i64 1616}
!82 = !{!13, !5, i64 1620}
!83 = !{!13, !5, i64 1624}
!84 = !{!13, !6, i64 1736}
!85 = distinct !{!85, !22}
!86 = !{!13, !5, i64 2008}
!87 = !{!13, !5, i64 1720}
!88 = !{!13, !5, i64 1724}
!89 = !{!13, !5, i64 1728}
!90 = distinct !{!90, !22}
!91 = distinct !{!91, !22}
!92 = distinct !{!92, !22}
!93 = distinct !{!93, !22}
!94 = distinct !{!94, !22}
!95 = distinct !{!95, !22}
!96 = distinct !{!96, !22}
!97 = distinct !{!97, !22}
!98 = distinct !{!98, !22}
!99 = distinct !{!99, !22}
!100 = !{!13, !5, i64 1656}
!101 = !{!13, !5, i64 1708}
!102 = !{!13, !10, i64 1912}
!103 = distinct !{!103, !22}
!104 = !{!13, !10, i64 1848}
