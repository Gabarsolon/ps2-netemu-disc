; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@hddlog_init.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@hddlog_write.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@.str = private unnamed_addr constant [24 x i8] c"boot: ps2_netemu_p11_W2\00", align 1
@.str.1 = private unnamed_addr constant [15 x i8] c"scan: rom_cnt=\00", align 1
@.str.2 = private unnamed_addr constant [6 x i8] c" hdd=\00", align 1
@.str.3 = private unnamed_addr constant [13 x i8] c" bus=4 dev=2\00", align 1
@.str.4 = private unnamed_addr constant [33 x i8] c"grd reject: sanity failed (0 hc)\00", align 1
@.str.5 = private unnamed_addr constant [44 x i8] c"finish: ps2_netemu_p11_W2 rejected by guard\00", align 1
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
@.str.16 = private unnamed_addr constant [4 x i8] c"tur\00", align 1
@.str.17 = private unnamed_addr constant [4 x i8] c"inq\00", align 1
@.str.18 = private unnamed_addr constant [4 x i8] c"cap\00", align 1
@.str.19 = private unnamed_addr constant [3 x i8] c"p2\00", align 1
@.str.20 = private unnamed_addr constant [4 x i8] c"p10\00", align 1
@.str.21 = private unnamed_addr constant [7 x i8] c"p10_p0\00", align 1
@.str.22 = private unnamed_addr constant [27 x i8] c"auth skipped: guard failed\00", align 1
@.str.23 = private unnamed_addr constant [9 x i8] c"get_cfg1\00", align 1
@.str.24 = private unnamed_addr constant [17 x i8] c"read_disc_struct\00", align 1
@.str.25 = private unnamed_addr constant [9 x i8] c"get_cfg2\00", align 1
@.str.26 = private unnamed_addr constant [33 x i8] c"pre auth_write: port=10 len=0x70\00", align 1
@.str.27 = private unnamed_addr constant [21 x i8] c"post auth_write: rc=\00", align 1
@.str.28 = private unnamed_addr constant [8 x i8] c" bytes=\00", align 1
@.str.29 = private unnamed_addr constant [36 x i8] c"pre auth_read: port=10 max_len=0x70\00", align 1
@.str.30 = private unnamed_addr constant [22 x i8] c"post auth_read: read=\00", align 1
@.str.31 = private unnamed_addr constant [8 x i8] c" polls=\00", align 1
@.str.32 = private unnamed_addr constant [9 x i8] c" stat=0x\00", align 1
@.str.33 = private unnamed_addr constant [8 x i8] c" flg=0x\00", align 1
@.str.34 = private unnamed_addr constant [6 x i8] c" vrd=\00", align 1
@.str.35 = private unnamed_addr constant [7 x i8] c"pio_16\00", align 1
@.str.36 = private unnamed_addr constant [6 x i8] c"pio_0\00", align 1
@.str.37 = private unnamed_addr constant [7 x i8] c"pio_17\00", align 1
@.str.38 = private unnamed_addr constant [7 x i8] c"dma_16\00", align 1
@.str.39 = private unnamed_addr constant [18 x i8] c"pre unmap: rgn=0x\00", align 1
@.str.40 = private unnamed_addr constant [14 x i8] c" len=0x100000\00", align 1
@.str.41 = private unnamed_addr constant [16 x i8] c"post unmap: rc=\00", align 1
@.str.42 = private unnamed_addr constant [17 x i8] c"pre free: rgn=0x\00", align 1
@.str.43 = private unnamed_addr constant [15 x i8] c"post free: rc=\00", align 1
@.str.44 = private unnamed_addr constant [23 x i8] c"pre close: bus=4 dev=2\00", align 1
@.str.45 = private unnamed_addr constant [16 x i8] c"post close: rc=\00", align 1
@.str.46 = private unnamed_addr constant [27 x i8] c"finish: ps2_netemu_p11_W2 \00", align 1
@.str.47 = private unnamed_addr constant [14 x i8] c"clean success\00", align 1
@.str.48 = private unnamed_addr constant [13 x i8] c"step failed=\00", align 1
@HEX_DIGITS = internal unnamed_addr constant [17 x i8] c"0123456789abcdef\00", align 1
@.str.49 = private unnamed_addr constant [5 x i8] c"pre \00", align 1
@.str.50 = private unnamed_addr constant [14 x i8] c": cmd_lpar=0x\00", align 1
@.str.51 = private unnamed_addr constant [13 x i8] c" buf_lpar=0x\00", align 1
@.str.52 = private unnamed_addr constant [6 x i8] c"post \00", align 1
@.str.53 = private unnamed_addr constant [11 x i8] c": send_rc=\00", align 1
@.str.54 = private unnamed_addr constant [10 x i8] c"timeout: \00", align 1
@.str.55 = private unnamed_addr constant [31 x i8] c" timed out; halting hypercalls\00", align 1
@.str.56 = private unnamed_addr constant [16 x i8] c": rc=0 async=0x\00", align 1
@.str.57 = private unnamed_addr constant [11 x i8] c"pre vuart_\00", align 1
@.str.58 = private unnamed_addr constant [12 x i8] c"post vuart_\00", align 1
@.str.59 = private unnamed_addr constant [6 x i8] c": rc=\00", align 1
@.str.60 = private unnamed_addr constant [8 x i8] c" val=0x\00", align 1
@auth_verdict_to_str.STRS = internal unnamed_addr constant [7 x ptr] [ptr @.str.61, ptr @.str.62, ptr @.str.63, ptr @.str.64, ptr @.str.65, ptr @.str.66, ptr @.str.67], align 8
@.str.61 = private unnamed_addr constant [5 x i8] c"NONE\00", align 1
@.str.62 = private unnamed_addr constant [3 x i8] c"OK\00", align 1
@.str.63 = private unnamed_addr constant [9 x i8] c"ERR_STAT\00", align 1
@.str.64 = private unnamed_addr constant [8 x i8] c"TIMEOUT\00", align 1
@.str.65 = private unnamed_addr constant [6 x i8] c"SHORT\00", align 1
@.str.66 = private unnamed_addr constant [8 x i8] c"SKIPPED\00", align 1
@.str.67 = private unnamed_addr constant [10 x i8] c"ERR_WRITE\00", align 1
@.str.68 = private unnamed_addr constant [7 x i8] c": lba=\00", align 1
@.str.69 = private unnamed_addr constant [8 x i8] c" proto=\00", align 1
@.str.70 = private unnamed_addr constant [7 x i8] c" blks=\00", align 1
@.str.71 = private unnamed_addr constant [6 x i8] c" bsz=\00", align 1
@.str.72 = private unnamed_addr constant [10 x i8] c" async=0x\00", align 1
@.str.73 = private unnamed_addr constant [6 x i8] c" cls=\00", align 1
@.str.74 = private unnamed_addr constant [5 x i8] c" a5=\00", align 1
@.str.75 = private unnamed_addr constant [5 x i8] c" w0=\00", align 1
@.str.76 = private unnamed_addr constant [6 x i8] c" w16=\00", align 1
@.str.77 = private unnamed_addr constant [7 x i8] c" vol='\00", align 1
@.str.78 = private unnamed_addr constant [2 x i8] c"'\00", align 1
@class_to_str.STRS = internal unnamed_addr constant [4 x ptr] [ptr @.str.79, ptr @.str.80, ptr @.str.81, ptr @.str.82], align 8
@.str.79 = private unnamed_addr constant [10 x i8] c"UNCHANGED\00", align 1
@.str.80 = private unnamed_addr constant [6 x i8] c"ZEROS\00", align 1
@.str.81 = private unnamed_addr constant [8 x i8] c"DATA_OK\00", align 1
@.str.82 = private unnamed_addr constant [6 x i8] c"OTHER\00", align 1
@.str.83 = private unnamed_addr constant [6 x i8] c"sense\00", align 1
@.str.84 = private unnamed_addr constant [14 x i8] c"P11-W2 AUTH: \00", align 1
@.str.85 = private unnamed_addr constant [7 x i8] c" ST=0x\00", align 1
@.str.86 = private unnamed_addr constant [7 x i8] c" FL=0x\00", align 1
@.str.87 = private unnamed_addr constant [9 x i8] c"PROF1=0x\00", align 1
@.str.88 = private unnamed_addr constant [10 x i8] c" PROF2=0x\00", align 1
@.str.89 = private unnamed_addr constant [8 x i8] c" RDS=0x\00", align 1
@.str.90 = private unnamed_addr constant [12 x i8] c"AUTH: READ=\00", align 1
@.str.91 = private unnamed_addr constant [8 x i8] c" POLLS=\00", align 1
@.str.92 = private unnamed_addr constant [5 x i8] c" WR=\00", align 1
@.str.93 = private unnamed_addr constant [8 x i8] c"PIO16: \00", align 1
@.str.94 = private unnamed_addr constant [5 x i8] c" A5=\00", align 1
@.str.95 = private unnamed_addr constant [4 x i8] c"HC=\00", align 1
@.str.96 = private unnamed_addr constant [6 x i8] c" LOG=\00", align 1
@.str.97 = private unnamed_addr constant [7 x i8] c" SKIP=\00", align 1
@.str.98 = private unnamed_addr constant [8 x i8] c" TMO=0x\00", align 1
@.str.99 = private unnamed_addr constant [12 x i8] c"PIO: 16_A5=\00", align 1
@.str.100 = private unnamed_addr constant [7 x i8] c" 0_A5=\00", align 1
@.str.101 = private unnamed_addr constant [8 x i8] c" 17_A5=\00", align 1
@.str.102 = private unnamed_addr constant [14 x i8] c"CDVD LPAR: 0x\00", align 1
@.str.103 = private unnamed_addr constant [11 x i8] c"DMA RGN=0x\00", align 1
@.str.104 = private unnamed_addr constant [8 x i8] c" BUS=0x\00", align 1
@.str.105 = private unnamed_addr constant [15 x i8] c"P11-W2 RUNNING\00", align 1

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
  %10 = tail call i64 @native_clock() #8
  %11 = getelementptr inbounds nuw i8, ptr %5, i64 1784
  store volatile i64 %10, ptr %11, align 8, !tbaa !14
  %12 = getelementptr inbounds nuw i8, ptr %5, i64 1672
  store volatile i32 1, ptr %12, align 8, !tbaa !15
  %13 = getelementptr inbounds nuw i8, ptr %5, i64 1676
  store volatile i32 0, ptr %13, align 4, !tbaa !16
  %14 = tail call fastcc signext i32 @wait_hdd_log_safe(i32 noundef zeroext 50) #9
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
  %20 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_init.path) #8
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
  %39 = tail call i64 @stock_raw_write(i32 noundef signext %20, i64 noundef 0, ptr noundef nonnull %5, i64 noundef 512) #8
  %40 = icmp eq i64 %39, 512
  %41 = tail call signext i32 @stock_ufs_close(i32 noundef signext %20) #8
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
  %50 = tail call fastcc signext i32 @wait_hdd_log_safe(i32 noundef zeroext 10) #9
  %51 = icmp eq i32 %50, 0
  br i1 %51, label %56, label %52

52:                                               ; preds = %49
  %53 = tail call signext i32 @stock_hdd_cache_flush() #8
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

; Function Attrs: minsize nounwind optsize
define internal fastcc signext range(i32 0, 2) i32 @wait_hdd_log_safe(i32 noundef zeroext range(i32 10, 51) %0) unnamed_addr #0 {
  br label %2

2:                                                ; preds = %32, %1
  %3 = phi i32 [ 0, %1 ], [ %33, %32 ]
  %4 = icmp eq i32 %3, %0
  br i1 %4, label %34, label %5

5:                                                ; preds = %2
  %6 = load i8, ptr inttoptr (i64 37865685 to ptr), align 1, !tbaa !23
  %7 = load i8, ptr inttoptr (i64 37865672 to ptr), align 8, !tbaa !23
  %8 = load volatile i64, ptr inttoptr (i64 37865568 to ptr), align 32, !tbaa !19
  %9 = load volatile i64, ptr inttoptr (i64 37865608 to ptr), align 8, !tbaa !19
  %10 = load volatile i64, ptr inttoptr (i64 37865616 to ptr), align 16, !tbaa !19
  %11 = load volatile i64, ptr inttoptr (i64 37865624 to ptr), align 8, !tbaa !19
  %12 = icmp eq i8 %6, 1
  %13 = icmp eq i8 %7, 0
  %14 = select i1 %12, i1 %13, i1 false
  %15 = icmp eq i64 %8, 3
  %16 = select i1 %14, i1 %15, i1 false
  %17 = icmp eq i64 %11, 0
  %18 = select i1 %16, i1 %17, i1 false
  %19 = icmp eq i64 %9, 0
  %20 = select i1 %18, i1 %19, i1 false
  %21 = icmp eq i64 %10, 0
  %22 = select i1 %20, i1 %21, i1 false
  br i1 %22, label %23, label %26

23:                                               ; preds = %5
  %24 = load i32, ptr inttoptr (i64 50680192 to ptr), align 128, !tbaa !20
  %25 = icmp eq i32 %24, 0
  br i1 %25, label %34, label %26

26:                                               ; preds = %5, %23
  %27 = tail call i64 @native_clock() #8
  br label %28

28:                                               ; preds = %28, %26
  %29 = tail call i64 @native_clock() #8
  %30 = sub i64 %29, %27
  %31 = icmp ult i64 %30, 79800
  br i1 %31, label %28, label %32, !llvm.loop !24

32:                                               ; preds = %28
  %33 = add nuw nsw i32 %3, 1
  br label %2, !llvm.loop !25

34:                                               ; preds = %2, %23
  %35 = phi i32 [ 1, %23 ], [ 0, %2 ]
  ret i32 %35
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
  br i1 %6, label %102, label %7

7:                                                ; preds = %4
  %8 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %9 = inttoptr i64 %8 to ptr
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 1668
  %11 = load volatile i32, ptr %10, align 4, !tbaa !12
  %12 = icmp eq i32 %11, 0
  br i1 %12, label %102, label %13

13:                                               ; preds = %7
  %14 = getelementptr inbounds nuw i8, ptr %9, i64 1672
  %15 = load volatile i32, ptr %14, align 8, !tbaa !15
  %16 = icmp ugt i32 %15, 127
  br i1 %16, label %17, label %18

17:                                               ; preds = %13
  store volatile i8 8, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

18:                                               ; preds = %13
  %19 = tail call fastcc signext i32 @wait_hdd_log_safe(i32 noundef zeroext 50) #9
  %20 = icmp eq i32 %19, 0
  br i1 %20, label %21, label %24

21:                                               ; preds = %18
  %22 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %23 = add i16 %22, 1
  store volatile i16 %23, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  br label %102

24:                                               ; preds = %18
  %25 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_write.path) #8
  %26 = icmp ugt i32 %25, 7
  br i1 %26, label %27, label %30

27:                                               ; preds = %24
  %28 = icmp eq i32 %25, -2
  %29 = select i1 %28, i8 2, i8 6
  store volatile i8 %29, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

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
  %43 = tail call i64 @native_clock() #8
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
  br label %52, !llvm.loop !26

62:                                               ; preds = %52, %35
  %63 = phi i64 [ 0, %35 ], [ %53, %52 ]
  %64 = getelementptr inbounds nuw i8, ptr %50, i64 %63
  store i8 0, ptr %64, align 1, !tbaa !23
  %65 = load volatile i32, ptr %14, align 8, !tbaa !15
  %66 = zext i32 %65 to i64
  %67 = shl nuw nsw i64 %66, 9
  %68 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef %67, ptr noundef nonnull %31, i64 noundef 512) #8
  %69 = icmp eq i64 %68, 512
  br i1 %69, label %75, label %73

70:                                               ; preds = %32
  %71 = getelementptr inbounds nuw [8 x i8], ptr %31, i64 %33
  store volatile i64 0, ptr %71, align 8, !tbaa !19
  %72 = add nuw nsw i64 %33, 1
  br label %32, !llvm.loop !27

73:                                               ; preds = %62
  %74 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #8
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

75:                                               ; preds = %62
  %76 = load volatile i32, ptr %14, align 8, !tbaa !15
  %77 = add i32 %76, 1
  %78 = getelementptr inbounds nuw i8, ptr %9, i64 28
  store volatile i32 %77, ptr %78, align 4, !tbaa !20
  %79 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !28
  %80 = add i32 %79, 1
  %81 = getelementptr inbounds nuw i8, ptr %9, i64 44
  store volatile i32 %80, ptr %81, align 4, !tbaa !20
  %82 = icmp eq i32 %0, 1162757152
  br i1 %82, label %83, label %85

83:                                               ; preds = %75
  %84 = getelementptr inbounds nuw i8, ptr %9, i64 40
  store volatile i32 1, ptr %84, align 8, !tbaa !20
  store volatile i8 1, ptr inttoptr (i64 9637743 to ptr), align 1, !tbaa !29
  br label %85

85:                                               ; preds = %83, %75
  %86 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef 0, ptr noundef nonnull %9, i64 noundef 512) #8
  %87 = icmp eq i64 %86, 512
  %88 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #8
  br i1 %87, label %90, label %89

89:                                               ; preds = %85
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

90:                                               ; preds = %85
  %91 = icmp eq i32 %88, 0
  br i1 %91, label %93, label %92

92:                                               ; preds = %90
  store volatile i8 6, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

93:                                               ; preds = %90
  store volatile i32 %77, ptr %14, align 8, !tbaa !15
  %94 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !28
  %95 = add i32 %94, 1
  store volatile i32 %95, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !28
  %96 = tail call fastcc signext i32 @wait_hdd_log_safe(i32 noundef zeroext 10) #9
  %97 = icmp eq i32 %96, 0
  br i1 %97, label %102, label %98

98:                                               ; preds = %93
  %99 = tail call signext i32 @stock_hdd_cache_flush() #8
  %100 = icmp eq i32 %99, 0
  br i1 %100, label %102, label %101

101:                                              ; preds = %98
  store volatile i8 7, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %102

102:                                              ; preds = %17, %21, %7, %73, %92, %98, %101, %93, %89, %27, %4
  %103 = phi i32 [ -1, %4 ], [ -1, %17 ], [ -1, %7 ], [ 0, %21 ], [ -1, %27 ], [ -1, %73 ], [ -1, %89 ], [ -1, %92 ], [ 0, %98 ], [ 0, %101 ], [ 0, %93 ]
  ret i32 %103
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
  %11 = tail call fastcc ptr @get_arena() #9
  %12 = icmp eq ptr %11, null
  br i1 %12, label %13, label %36

13:                                               ; preds = %1
  %14 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %15 = and i32 %14, 8
  %16 = icmp eq i32 %15, 0
  br i1 %16, label %17, label %595

17:                                               ; preds = %13
  %18 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %19 = or i32 %18, 1
  store volatile i32 %19, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %20 = tail call i64 @native_alloc(i64 noundef 4096, i64 noundef 3, i64 noundef 0) #8
  %21 = tail call fastcc signext i32 @arena_rw(i64 noundef %20) #9
  %22 = icmp eq i32 %21, 0
  br i1 %22, label %33, label %23

23:                                               ; preds = %17
  store volatile i64 %20, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %24 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %25 = or i32 %24, 4
  store volatile i32 %25, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %26 = inttoptr i64 %20 to ptr
  br label %27

27:                                               ; preds = %30, %23
  %28 = phi i64 [ %32, %30 ], [ 0, %23 ]
  %29 = icmp eq i64 %28, 2216
  br i1 %29, label %36, label %30

30:                                               ; preds = %27
  %31 = getelementptr inbounds nuw i8, ptr %26, i64 %28
  store volatile i8 0, ptr %31, align 1, !tbaa !23
  %32 = add nuw nsw i64 %28, 1
  br label %27, !llvm.loop !31

33:                                               ; preds = %17
  %34 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %35 = or i32 %34, 8
  store volatile i32 %35, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  br label %595

36:                                               ; preds = %27, %1
  %37 = phi ptr [ %11, %1 ], [ %26, %27 ]
  %38 = tail call i64 @native_clock() #8
  %39 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !32
  store volatile i64 %38, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !32
  %40 = icmp ne i64 %39, 0
  %41 = sub i64 %38, %39
  %42 = icmp ugt i64 %41, 119700000
  %43 = select i1 %40, i1 %42, i1 false
  br i1 %43, label %44, label %47

44:                                               ; preds = %36
  %45 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !33
  %46 = add i32 %45, 1
  store volatile i32 %46, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !33
  br label %47

47:                                               ; preds = %44, %36
  %48 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %49 = and i32 %48, 2
  %50 = icmp eq i32 %49, 0
  br i1 %50, label %51, label %522

51:                                               ; preds = %47
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #10
  %52 = tail call signext i32 @hddlog_init() #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str) #9
  %53 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %53, align 1, !tbaa !23
  %54 = call signext i32 @hddlog_write(i32 noundef zeroext 1112493908, i64 noundef 2216, i64 noundef 2, ptr noundef nonnull %3) #9
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
  store volatile i32 %58, ptr %64, align 8, !tbaa !37
  store volatile i32 %61, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !38
  store volatile i32 %60, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !39
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.1) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %61) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.2) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %60) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.3) #9
  %65 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %65, align 1, !tbaa !23
  %66 = zext i32 %61 to i64
  %67 = zext nneg i32 %60 to i64
  %68 = call signext i32 @hddlog_write(i32 noundef zeroext 1396916558, i64 noundef %66, i64 noundef %67, ptr noundef nonnull %3) #9
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
  br i1 %78, label %101, label %106

79:                                               ; preds = %56
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #10
  store i64 0, ptr %5, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #10
  store i64 0, ptr %6, align 8, !tbaa !19
  %80 = or disjoint i64 %57, 7234318118812647424
  %81 = call i64 @repo_read(ptr noundef nonnull %5, ptr noundef nonnull %6, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8392862959675637760, i64 noundef 0) #8
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
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #10
  store i64 0, ptr %7, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #10
  store i64 0, ptr %8, align 8, !tbaa !19
  %88 = call i64 @repo_read(ptr noundef nonnull %7, ptr noundef nonnull %8, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8243108395510267904, i64 noundef 0) #8
  %89 = icmp eq i64 %88, 0
  br i1 %89, label %90, label %93

90:                                               ; preds = %86
  %91 = load i64, ptr %7, align 8, !tbaa !19
  %92 = trunc i64 %91 to i32
  store volatile i32 %92, ptr %55, align 4, !tbaa !40
  br label %93

93:                                               ; preds = %90, %86
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #10
  br label %95

94:                                               ; preds = %83
  br label %95

95:                                               ; preds = %94, %93, %83, %79
  %96 = phi i32 [ %84, %93 ], [ %84, %94 ], [ %84, %83 ], [ %58, %79 ]
  %97 = phi i64 [ %57, %93 ], [ %59, %94 ], [ %59, %83 ], [ %59, %79 ]
  %98 = phi i32 [ %60, %93 ], [ 1, %94 ], [ %60, %83 ], [ %60, %79 ]
  %99 = phi i32 [ %87, %93 ], [ %61, %94 ], [ %61, %83 ], [ %61, %79 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #10
  %100 = add nuw nsw i64 %57, 1
  br label %56, !llvm.loop !41

101:                                              ; preds = %63
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  store volatile i32 -1, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.4) #9
  %102 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %102, align 1, !tbaa !23
  %103 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.5) #9
  %104 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %104, align 1, !tbaa !23
  %105 = call signext i32 @hddlog_write(i32 noundef zeroext 1162757152, i64 noundef 1, i64 noundef 0, ptr noundef nonnull %3) #9
  br label %519

106:                                              ; preds = %63
  %107 = getelementptr inbounds nuw i8, ptr %37, i64 1760
  store volatile i64 %69, ptr %107, align 8, !tbaa !44
  %108 = getelementptr inbounds nuw i8, ptr %37, i64 1768
  store volatile i64 %70, ptr %108, align 8, !tbaa !45
  %109 = getelementptr inbounds nuw i8, ptr %37, i64 1776
  store volatile i64 %71, ptr %109, align 8, !tbaa !46
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.6) #9
  %110 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %110, align 1, !tbaa !23
  %111 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.7) #9
  %112 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %112, align 1, !tbaa !23
  %113 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #9
  %114 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %115 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %116 = add i32 %115, 1
  store volatile i32 %116, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %117 = trunc i64 %114 to i32
  %118 = getelementptr inbounds nuw i8, ptr %37, i64 1604
  store volatile i32 %117, ptr %118, align 4, !tbaa !48
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.8) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %117) #9
  %119 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %119, align 1, !tbaa !23
  %120 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %114, i64 noundef 0, ptr noundef nonnull %3) #9
  %121 = icmp eq i64 %114, 0
  br i1 %121, label %123, label %122

122:                                              ; preds = %106
  store volatile i32 2, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  store volatile i32 %117, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  br label %506

123:                                              ; preds = %106
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.9) #9
  %124 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %124, align 1, !tbaa !23
  %125 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 1048576, i64 noundef 20, ptr noundef nonnull %3) #9
  %126 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef %59, i64 noundef 1048576, i64 noundef 20, i64 noundef 0, i64 noundef 0) #8
  %127 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %128 = add i32 %127, 1
  store volatile i32 %128, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %129 = trunc i64 %126 to i32
  %130 = getelementptr inbounds nuw i8, ptr %37, i64 1608
  store volatile i32 %129, ptr %130, align 8, !tbaa !49
  %131 = icmp eq i64 %126, 0
  br i1 %131, label %135, label %132

132:                                              ; preds = %123
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.10) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %129) #9
  %133 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %133, align 1, !tbaa !23
  %134 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %126, i64 noundef 0, ptr noundef nonnull %3) #9
  store volatile i32 3, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  store volatile i32 %129, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  br label %496

135:                                              ; preds = %123
  %136 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %137 = getelementptr inbounds nuw i8, ptr %37, i64 1744
  store volatile i64 %136, ptr %137, align 8, !tbaa !51
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.11) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %136) #9
  %138 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %138, align 1, !tbaa !23
  %139 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef 0, i64 noundef %136, ptr noundef nonnull %3) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.12) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %69) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.13) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %136) #9
  %140 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %140, align 1, !tbaa !23
  %141 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %69, i64 noundef %136, ptr noundef nonnull %3) #9
  %142 = call i64 @lv1_hcall(i64 noundef 176, i64 noundef 4, i64 noundef %59, i64 noundef %69, i64 noundef %136, i64 noundef 1048576, i64 noundef -2305843009213691904) #8
  %143 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %144 = add i32 %143, 1
  store volatile i32 %144, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %145 = trunc i64 %142 to i32
  %146 = getelementptr inbounds nuw i8, ptr %37, i64 1612
  store volatile i32 %145, ptr %146, align 4, !tbaa !52
  %147 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %148 = getelementptr inbounds nuw i8, ptr %37, i64 1752
  store volatile i64 %147, ptr %148, align 8, !tbaa !53
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.14) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %145) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.15) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %147) #9
  %149 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %149, align 1, !tbaa !23
  %150 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %142, i64 noundef %147, ptr noundef nonnull %3) #9
  %151 = icmp eq i64 %142, 0
  br i1 %151, label %153, label %152

152:                                              ; preds = %135
  store volatile i32 4, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  store volatile i32 %145, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  br label %486

153:                                              ; preds = %135
  %154 = inttoptr i64 %70 to ptr
  %155 = or disjoint i64 %70, 4096
  %156 = inttoptr i64 %155 to ptr
  %157 = or disjoint i64 %69, 4096
  %158 = getelementptr inbounds nuw i8, ptr %37, i64 1628
  %159 = getelementptr inbounds nuw i8, ptr %37, i64 1792
  %160 = getelementptr inbounds nuw i8, ptr %37, i64 1680
  %161 = getelementptr inbounds nuw i8, ptr %37, i64 1856
  %162 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 5, i32 noundef zeroext 1, ptr noundef nonnull @.str.16, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %158, ptr noundef nonnull %159, ptr noundef nonnull %160, ptr noundef nonnull %161) #9
  %163 = icmp eq i32 %162, 1
  br i1 %163, label %506, label %164

164:                                              ; preds = %153
  %165 = getelementptr inbounds nuw i8, ptr %37, i64 1632
  %166 = getelementptr inbounds nuw i8, ptr %37, i64 1800
  %167 = getelementptr inbounds nuw i8, ptr %37, i64 1684
  %168 = getelementptr inbounds nuw i8, ptr %37, i64 1864
  %169 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext 18, i32 noundef zeroext 36, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 6, i32 noundef zeroext 2, ptr noundef nonnull @.str.17, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %165, ptr noundef nonnull %166, ptr noundef nonnull %167, ptr noundef nonnull %168) #9
  %170 = icmp eq i32 %169, 1
  br i1 %170, label %506, label %171

171:                                              ; preds = %164
  %172 = getelementptr inbounds nuw i8, ptr %37, i64 1920
  br label %173

173:                                              ; preds = %183, %171
  %174 = phi i64 [ 0, %171 ], [ %187, %183 ]
  %175 = icmp eq i64 %174, 36
  br i1 %175, label %176, label %183

176:                                              ; preds = %173
  %177 = getelementptr inbounds nuw i8, ptr %37, i64 1636
  %178 = getelementptr inbounds nuw i8, ptr %37, i64 1808
  %179 = getelementptr inbounds nuw i8, ptr %37, i64 1688
  %180 = getelementptr inbounds nuw i8, ptr %37, i64 1872
  %181 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext 37, i32 noundef zeroext 8, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 7, i32 noundef zeroext 4, ptr noundef nonnull @.str.18, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %177, ptr noundef nonnull %178, ptr noundef nonnull %179, ptr noundef nonnull %180) #9
  %182 = icmp eq i32 %181, 1
  br i1 %182, label %506, label %188

183:                                              ; preds = %173
  %184 = getelementptr inbounds nuw i8, ptr %156, i64 %174
  %185 = load volatile i8, ptr %184, align 1, !tbaa !23
  %186 = getelementptr inbounds nuw i8, ptr %172, i64 %174
  store volatile i8 %185, ptr %186, align 1, !tbaa !23
  %187 = add nuw nsw i64 %174, 1
  br label %173, !llvm.loop !54

188:                                              ; preds = %176
  %189 = load volatile i8, ptr %156, align 1, !tbaa !23
  %190 = zext i8 %189 to i32
  %191 = shl nuw i32 %190, 24
  %192 = getelementptr inbounds nuw i8, ptr %156, i64 1
  %193 = load volatile i8, ptr %192, align 1, !tbaa !23
  %194 = zext i8 %193 to i32
  %195 = shl nuw nsw i32 %194, 16
  %196 = or disjoint i32 %195, %191
  %197 = getelementptr inbounds nuw i8, ptr %156, i64 2
  %198 = load volatile i8, ptr %197, align 1, !tbaa !23
  %199 = zext i8 %198 to i32
  %200 = shl nuw nsw i32 %199, 8
  %201 = or disjoint i32 %196, %200
  %202 = getelementptr inbounds nuw i8, ptr %156, i64 3
  %203 = load volatile i8, ptr %202, align 1, !tbaa !23
  %204 = zext i8 %203 to i32
  %205 = or disjoint i32 %201, %204
  %206 = getelementptr inbounds nuw i8, ptr %37, i64 1712
  store volatile i32 %205, ptr %206, align 8, !tbaa !55
  %207 = getelementptr inbounds nuw i8, ptr %156, i64 4
  %208 = load volatile i8, ptr %207, align 1, !tbaa !23
  %209 = zext i8 %208 to i32
  %210 = shl nuw i32 %209, 24
  %211 = getelementptr inbounds nuw i8, ptr %156, i64 5
  %212 = load volatile i8, ptr %211, align 1, !tbaa !23
  %213 = zext i8 %212 to i32
  %214 = shl nuw nsw i32 %213, 16
  %215 = or disjoint i32 %214, %210
  %216 = getelementptr inbounds nuw i8, ptr %156, i64 6
  %217 = load volatile i8, ptr %216, align 1, !tbaa !23
  %218 = zext i8 %217 to i32
  %219 = shl nuw nsw i32 %218, 8
  %220 = or disjoint i32 %215, %219
  %221 = getelementptr inbounds nuw i8, ptr %156, i64 7
  %222 = load volatile i8, ptr %221, align 1, !tbaa !23
  %223 = zext i8 %222 to i32
  %224 = or disjoint i32 %220, %223
  %225 = getelementptr inbounds nuw i8, ptr %37, i64 1716
  store volatile i32 %224, ptr %225, align 4, !tbaa !56
  %226 = getelementptr inbounds nuw i8, ptr %37, i64 2008
  %227 = getelementptr inbounds nuw i8, ptr %37, i64 2032
  call fastcc void @query_vuart_param(i64 noundef 2, i64 noundef 3, ptr noundef nonnull %226, ptr noundef nonnull %227, ptr noundef nonnull @.str.19) #9
  %228 = getelementptr inbounds nuw i8, ptr %37, i64 2012
  %229 = getelementptr inbounds nuw i8, ptr %37, i64 2040
  call fastcc void @query_vuart_param(i64 noundef 10, i64 noundef 3, ptr noundef nonnull %228, ptr noundef nonnull %229, ptr noundef nonnull @.str.20) #9
  %230 = load volatile i32, ptr %228, align 4, !tbaa !57
  %231 = sext i32 %230 to i64
  %232 = getelementptr inbounds nuw i8, ptr %37, i64 2016
  %233 = getelementptr inbounds nuw i8, ptr %37, i64 2048
  call fastcc void @query_vuart_param(i64 noundef 10, i64 noundef 0, ptr noundef nonnull %232, ptr noundef nonnull %233, ptr noundef nonnull @.str.21) #9
  %234 = load volatile i32, ptr %158, align 4, !tbaa !58
  %235 = icmp eq i32 %234, 0
  br i1 %235, label %236, label %239

236:                                              ; preds = %188
  %237 = load volatile i64, ptr %159, align 8, !tbaa !59
  %238 = icmp eq i64 %237, 0
  br i1 %238, label %240, label %239

239:                                              ; preds = %236, %188
  br label %240

240:                                              ; preds = %239, %236
  %241 = phi i32 [ 0, %239 ], [ 1, %236 ]
  %242 = load volatile i32, ptr %177, align 4, !tbaa !60
  %243 = icmp eq i32 %242, 0
  br i1 %243, label %244, label %247

244:                                              ; preds = %240
  %245 = load volatile i64, ptr %178, align 8, !tbaa !61
  %246 = icmp eq i64 %245, 0
  br i1 %246, label %248, label %247

247:                                              ; preds = %244, %240
  br label %248

248:                                              ; preds = %247, %244
  %249 = phi i32 [ 0, %247 ], [ %241, %244 ]
  %250 = load volatile i32, ptr %225, align 4, !tbaa !56
  %251 = icmp ne i32 %250, 2048
  %252 = icmp ne i32 %230, 0
  %253 = select i1 %252, i1 true, i1 %251
  %254 = icmp eq i32 %249, 0
  %255 = or i1 %254, %253
  br i1 %255, label %256, label %262

256:                                              ; preds = %248
  %257 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 5, ptr %257, align 8, !tbaa !62
  %258 = getelementptr inbounds nuw i8, ptr %37, i64 2073
  store volatile i8 1, ptr %258, align 1, !tbaa !63
  %259 = load volatile i32, ptr %225, align 4, !tbaa !56
  %260 = zext i32 %259 to i64
  %261 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %260, i64 noundef %231, ptr noundef nonnull @.str.22) #9
  br label %430

262:                                              ; preds = %248
  %263 = getelementptr inbounds nuw i8, ptr %37, i64 2112
  %264 = getelementptr inbounds nuw i8, ptr %37, i64 2120
  %265 = getelementptr inbounds nuw i8, ptr %37, i64 2128
  %266 = getelementptr inbounds nuw i8, ptr %37, i64 2136
  %267 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext 70, i32 noundef zeroext 32, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 16, i32 noundef zeroext 256, ptr noundef nonnull @.str.23, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %263, ptr noundef nonnull %264, ptr noundef nonnull %265, ptr noundef nonnull %266) #9
  %268 = icmp eq i32 %267, 1
  br i1 %268, label %506, label %269

269:                                              ; preds = %262
  %270 = load volatile i8, ptr %216, align 1, !tbaa !23
  %271 = zext i8 %270 to i16
  %272 = shl nuw i16 %271, 8
  %273 = load volatile i8, ptr %221, align 1, !tbaa !23
  %274 = zext i8 %273 to i16
  %275 = or disjoint i16 %272, %274
  %276 = getelementptr inbounds nuw i8, ptr %37, i64 2144
  store volatile i16 %275, ptr %276, align 8, !tbaa !64
  %277 = getelementptr inbounds nuw i8, ptr %37, i64 2148
  %278 = getelementptr inbounds nuw i8, ptr %37, i64 2152
  %279 = getelementptr inbounds nuw i8, ptr %37, i64 2160
  %280 = getelementptr inbounds nuw i8, ptr %37, i64 2168
  %281 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext -83, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 17, i32 noundef zeroext 512, ptr noundef nonnull @.str.24, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %277, ptr noundef nonnull %278, ptr noundef nonnull %279, ptr noundef nonnull %280) #9
  %282 = icmp eq i32 %281, 1
  br i1 %282, label %506, label %283

283:                                              ; preds = %269
  %284 = getelementptr inbounds nuw i8, ptr %37, i64 2176
  %285 = getelementptr inbounds nuw i8, ptr %37, i64 2184
  %286 = getelementptr inbounds nuw i8, ptr %37, i64 2192
  %287 = getelementptr inbounds nuw i8, ptr %37, i64 2200
  %288 = call fastcc signext i32 @execute_atapi_cmd(i64 noundef %59, i8 noundef zeroext 70, i32 noundef zeroext 32, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 18, i32 noundef zeroext 1024, ptr noundef nonnull @.str.25, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %284, ptr noundef nonnull %285, ptr noundef nonnull %286, ptr noundef nonnull %287) #9
  %289 = icmp eq i32 %288, 1
  br i1 %289, label %506, label %290

290:                                              ; preds = %283
  %291 = load volatile i8, ptr %216, align 1, !tbaa !23
  %292 = zext i8 %291 to i16
  %293 = shl nuw i16 %292, 8
  %294 = load volatile i8, ptr %221, align 1, !tbaa !23
  %295 = zext i8 %294 to i16
  %296 = or disjoint i16 %293, %295
  %297 = getelementptr inbounds nuw i8, ptr %37, i64 2208
  store volatile i16 %296, ptr %297, align 8, !tbaa !65
  %298 = or disjoint i64 %69, 6144
  %299 = getelementptr inbounds nuw i8, ptr %156, i64 2048
  %300 = getelementptr inbounds nuw i8, ptr %156, i64 2304
  call fastcc void @format_auth_request(ptr noundef nonnull %299) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.26) #9
  %301 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %301, align 1, !tbaa !23
  %302 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 10, i64 noundef 112, ptr noundef nonnull %3) #9
  %303 = call i64 @lv1_hcall(i64 noundef 163, i64 noundef 10, i64 noundef %298, i64 noundef 112, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %304 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %305 = add i32 %304, 1
  store volatile i32 %305, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %306 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %307 = trunc i64 %303 to i32
  %308 = getelementptr inbounds nuw i8, ptr %37, i64 2084
  store volatile i32 %307, ptr %308, align 4, !tbaa !66
  %309 = trunc i64 %306 to i32
  %310 = getelementptr inbounds nuw i8, ptr %37, i64 2088
  store volatile i32 %309, ptr %310, align 8, !tbaa !67
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.27) #9
  call fastcc void @format_s32(ptr noundef %4, i32 noundef signext %307) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.28) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %309) #9
  %311 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %311, align 1, !tbaa !23
  %312 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %303, i64 noundef %306, ptr noundef nonnull %3) #9
  %313 = icmp ne i64 %303, 0
  %314 = icmp eq i64 %306, 0
  %315 = select i1 %313, i1 true, i1 %314
  br i1 %315, label %316, label %318

316:                                              ; preds = %290
  %317 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 6, ptr %317, align 8, !tbaa !62
  br label %430

318:                                              ; preds = %290
  call fastcc void @prefill_buffer(ptr noundef nonnull %300, i32 noundef zeroext 112, i8 noundef zeroext 0) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.29) #9
  %319 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %319, align 1, !tbaa !23
  %320 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 10, i64 noundef 112, ptr noundef nonnull %3) #9
  %321 = call i64 @native_clock() #8
  %322 = getelementptr inbounds nuw i8, ptr %37, i64 2092
  %323 = or disjoint i64 %69, 6400
  br label %324

324:                                              ; preds = %339, %318
  %325 = phi i32 [ 0, %318 ], [ %329, %339 ]
  %326 = phi i32 [ 0, %318 ], [ %341, %339 ]
  %327 = icmp ult i32 %326, 112
  br i1 %327, label %328, label %345

328:                                              ; preds = %324
  %329 = add i32 %325, 1
  %330 = zext nneg i32 %326 to i64
  %331 = or disjoint i64 %330, %323
  %332 = sub nuw nsw i64 112, %330
  %333 = call i64 @lv1_hcall(i64 noundef 162, i64 noundef 10, i64 noundef %331, i64 noundef %332, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %334 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %335 = add i32 %334, 1
  store volatile i32 %335, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %336 = trunc i64 %333 to i32
  store volatile i32 %336, ptr %322, align 4, !tbaa !68
  %337 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %338 = icmp eq i64 %333, 0
  br i1 %338, label %339, label %345

339:                                              ; preds = %328
  %340 = trunc i64 %337 to i32
  %341 = add i32 %326, %340
  %342 = call i64 @native_clock() #8
  %343 = sub i64 %342, %321
  %344 = icmp ugt i64 %343, 159599999
  br i1 %344, label %345, label %324

345:                                              ; preds = %339, %328, %324
  %346 = phi i32 [ %325, %324 ], [ %329, %328 ], [ %329, %339 ]
  %347 = phi i32 [ %326, %324 ], [ %326, %328 ], [ %341, %339 ]
  %348 = getelementptr inbounds nuw i8, ptr %37, i64 2096
  store volatile i32 %347, ptr %348, align 8, !tbaa !69
  %349 = getelementptr inbounds nuw i8, ptr %37, i64 2100
  store volatile i32 %346, ptr %349, align 4, !tbaa !70
  %350 = call i64 @native_clock() #8
  %351 = sub i64 %350, %321
  %352 = getelementptr inbounds nuw i8, ptr %37, i64 2104
  store volatile i64 %351, ptr %352, align 8, !tbaa !71
  %353 = icmp ugt i32 %347, 3
  br i1 %353, label %354, label %401

354:                                              ; preds = %345
  %355 = load volatile i8, ptr %300, align 1, !tbaa !23
  %356 = zext i8 %355 to i32
  %357 = shl nuw i32 %356, 24
  %358 = getelementptr inbounds nuw i8, ptr %156, i64 2305
  %359 = load volatile i8, ptr %358, align 1, !tbaa !23
  %360 = zext i8 %359 to i32
  %361 = shl nuw nsw i32 %360, 16
  %362 = or disjoint i32 %361, %357
  %363 = getelementptr inbounds nuw i8, ptr %156, i64 2306
  %364 = load volatile i8, ptr %363, align 1, !tbaa !23
  %365 = zext i8 %364 to i32
  %366 = shl nuw nsw i32 %365, 8
  %367 = or disjoint i32 %362, %366
  %368 = getelementptr inbounds nuw i8, ptr %156, i64 2307
  %369 = load volatile i8, ptr %368, align 1, !tbaa !23
  %370 = zext i8 %369 to i32
  %371 = or disjoint i32 %367, %370
  %372 = getelementptr inbounds nuw i8, ptr %37, i64 2080
  store volatile i32 %371, ptr %372, align 8, !tbaa !72
  %373 = icmp ugt i32 %347, 35
  br i1 %373, label %374, label %405

374:                                              ; preds = %354
  %375 = getelementptr inbounds nuw i8, ptr %156, i64 2338
  %376 = load volatile i8, ptr %375, align 1, !tbaa !23
  %377 = zext i8 %376 to i16
  %378 = shl nuw i16 %377, 8
  %379 = getelementptr inbounds nuw i8, ptr %156, i64 2339
  %380 = load volatile i8, ptr %379, align 1, !tbaa !23
  %381 = zext i8 %380 to i16
  %382 = or disjoint i16 %378, %381
  %383 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  store volatile i16 %382, ptr %383, align 2, !tbaa !73
  %384 = icmp ugt i32 %347, 56
  br i1 %384, label %385, label %405

385:                                              ; preds = %374
  %386 = getelementptr inbounds nuw i8, ptr %156, i64 2360
  %387 = load volatile i8, ptr %386, align 1, !tbaa !23
  %388 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  store volatile i8 %387, ptr %388, align 4, !tbaa !74
  %389 = icmp ugt i32 %347, 111
  br i1 %389, label %390, label %405

390:                                              ; preds = %385
  %391 = load volatile i16, ptr %383, align 2, !tbaa !73
  %392 = icmp eq i16 %391, 0
  br i1 %392, label %393, label %399

393:                                              ; preds = %390
  %394 = load volatile i8, ptr %388, align 4, !tbaa !74
  %395 = icmp eq i8 %394, 0
  %396 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  br i1 %395, label %398, label %397

397:                                              ; preds = %393
  store volatile i8 1, ptr %396, align 8, !tbaa !62
  br label %407

398:                                              ; preds = %393
  store volatile i8 2, ptr %396, align 8, !tbaa !62
  br label %407

399:                                              ; preds = %390
  %400 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 2, ptr %400, align 8, !tbaa !62
  br label %407

401:                                              ; preds = %345
  %402 = icmp eq i32 %347, 0
  br i1 %402, label %403, label %405

403:                                              ; preds = %401
  %404 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 3, ptr %404, align 8, !tbaa !62
  br label %407

405:                                              ; preds = %401, %385, %374, %354
  %406 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  store volatile i8 4, ptr %406, align 8, !tbaa !62
  br label %407

407:                                              ; preds = %405, %403, %399, %398, %397
  %408 = getelementptr inbounds nuw i8, ptr %156, i64 2368
  call fastcc void @prefill_buffer(ptr noundef nonnull %408, i32 noundef zeroext 48, i8 noundef zeroext 0) #9
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.30) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %347) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.31) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %346) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.32) #9
  %409 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  %410 = load volatile i16, ptr %409, align 2, !tbaa !73
  %411 = zext i16 %410 to i32
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %411) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.33) #9
  %412 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  %413 = load volatile i8, ptr %412, align 4, !tbaa !74
  %414 = zext i8 %413 to i32
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %414) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.34) #9
  %415 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  %416 = load volatile i8, ptr %415, align 8, !tbaa !62
  %417 = icmp ult i8 %416, 7
  br i1 %417, label %418, label %422

418:                                              ; preds = %407
  %419 = zext nneg i8 %416 to i64
  %420 = getelementptr inbounds nuw [8 x i8], ptr @auth_verdict_to_str.STRS, i64 %419
  %421 = load ptr, ptr %420, align 8, !tbaa !34
  br label %422

422:                                              ; preds = %418, %407
  %423 = phi ptr [ %421, %418 ], [ @.str.61, %407 ]
  call fastcc void @append_str(ptr noundef %4, ptr noundef %423) #9
  %424 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %424, align 1, !tbaa !23
  %425 = load volatile i16, ptr %409, align 2, !tbaa !73
  %426 = zext i16 %425 to i64
  %427 = load volatile i8, ptr %412, align 4, !tbaa !74
  %428 = zext i8 %427 to i64
  %429 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %426, i64 noundef %428, ptr noundef nonnull %3) #9
  br label %430

430:                                              ; preds = %422, %316, %256
  %431 = getelementptr inbounds nuw i8, ptr %37, i64 1640
  %432 = getelementptr inbounds nuw i8, ptr %37, i64 1816
  %433 = getelementptr inbounds nuw i8, ptr %37, i64 1692
  %434 = getelementptr inbounds nuw i8, ptr %37, i64 1880
  %435 = getelementptr inbounds nuw i8, ptr %37, i64 1720
  %436 = getelementptr inbounds nuw i8, ptr %37, i64 1736
  %437 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 16, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 8, i32 noundef zeroext 8, ptr noundef nonnull @.str.35, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %37, ptr noundef nonnull %431, ptr noundef nonnull %432, ptr noundef nonnull %433, ptr noundef nonnull %434, ptr noundef nonnull %435, ptr noundef nonnull %436) #9
  %438 = icmp eq i32 %437, 1
  br i1 %438, label %506, label %439

439:                                              ; preds = %430
  %440 = getelementptr inbounds nuw i8, ptr %37, i64 1974
  br label %441

441:                                              ; preds = %453, %439
  %442 = phi i64 [ 0, %439 ], [ %457, %453 ]
  %443 = icmp eq i64 %442, 32
  br i1 %443, label %444, label %453

444:                                              ; preds = %441
  %445 = getelementptr inbounds nuw i8, ptr %37, i64 1644
  %446 = getelementptr inbounds nuw i8, ptr %37, i64 1824
  %447 = getelementptr inbounds nuw i8, ptr %37, i64 1696
  %448 = getelementptr inbounds nuw i8, ptr %37, i64 1888
  %449 = getelementptr inbounds nuw i8, ptr %37, i64 1724
  %450 = getelementptr inbounds nuw i8, ptr %37, i64 1737
  %451 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 0, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 9, i32 noundef zeroext 16, ptr noundef nonnull @.str.36, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %37, ptr noundef nonnull %445, ptr noundef nonnull %446, ptr noundef nonnull %447, ptr noundef nonnull %448, ptr noundef nonnull %449, ptr noundef nonnull %450) #9
  %452 = icmp eq i32 %451, 1
  br i1 %452, label %506, label %458

453:                                              ; preds = %441
  %454 = getelementptr inbounds nuw i8, ptr %156, i64 %442
  %455 = load volatile i8, ptr %454, align 1, !tbaa !23
  %456 = getelementptr inbounds nuw i8, ptr %440, i64 %442
  store volatile i8 %455, ptr %456, align 1, !tbaa !23
  %457 = add nuw nsw i64 %442, 1
  br label %441, !llvm.loop !75

458:                                              ; preds = %444
  %459 = getelementptr inbounds nuw i8, ptr %37, i64 1648
  %460 = getelementptr inbounds nuw i8, ptr %37, i64 1832
  %461 = getelementptr inbounds nuw i8, ptr %37, i64 1700
  %462 = getelementptr inbounds nuw i8, ptr %37, i64 1896
  %463 = getelementptr inbounds nuw i8, ptr %37, i64 1728
  %464 = getelementptr inbounds nuw i8, ptr %37, i64 1738
  %465 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 17, i32 noundef zeroext 2048, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 10, i32 noundef zeroext 32, ptr noundef nonnull @.str.37, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %37, ptr noundef nonnull %459, ptr noundef nonnull %460, ptr noundef nonnull %461, ptr noundef nonnull %462, ptr noundef nonnull %463, ptr noundef nonnull %464) #9
  %466 = icmp eq i32 %465, 1
  br i1 %466, label %506, label %467

467:                                              ; preds = %458
  %468 = getelementptr inbounds nuw i8, ptr %37, i64 1652
  %469 = getelementptr inbounds nuw i8, ptr %37, i64 1840
  %470 = getelementptr inbounds nuw i8, ptr %37, i64 1704
  %471 = getelementptr inbounds nuw i8, ptr %37, i64 1904
  %472 = getelementptr inbounds nuw i8, ptr %37, i64 1732
  %473 = getelementptr inbounds nuw i8, ptr %37, i64 1739
  %474 = call fastcc signext i32 @execute_read_test(i64 noundef %59, i32 noundef zeroext 16, i32 noundef zeroext 1, i32 noundef zeroext 2048, i32 noundef zeroext 3, i32 noundef zeroext 11, i32 noundef zeroext 64, ptr noundef nonnull @.str.38, ptr noundef %154, i64 noundef %69, ptr noundef nonnull %156, i64 noundef %157, ptr noundef nonnull %37, ptr noundef nonnull %468, ptr noundef nonnull %469, ptr noundef nonnull %470, ptr noundef nonnull %471, ptr noundef nonnull %472, ptr noundef nonnull %473) #9
  %475 = icmp eq i32 %474, 1
  br i1 %475, label %506, label %476

476:                                              ; preds = %467
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.39) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %136) #9
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.40) #9
  %477 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %477, align 1, !tbaa !23
  %478 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %136, i64 noundef 1048576, ptr noundef nonnull %3) #9
  %479 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef %59, i64 noundef %136, i64 noundef 1048576, i64 noundef 0, i64 noundef 0) #8
  %480 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %481 = add i32 %480, 1
  store volatile i32 %481, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %482 = trunc i64 %479 to i32
  %483 = getelementptr inbounds nuw i8, ptr %37, i64 1616
  store volatile i32 %482, ptr %483, align 8, !tbaa !76
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.41) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %482) #9
  %484 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %484, align 1, !tbaa !23
  %485 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %479, i64 noundef 0, ptr noundef nonnull %3) #9
  br label %486

486:                                              ; preds = %476, %152
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.42) #9
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %136) #9
  %487 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %487, align 1, !tbaa !23
  %488 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %136, i64 noundef 0, ptr noundef nonnull %3) #9
  %489 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef %59, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %490 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %491 = add i32 %490, 1
  store volatile i32 %491, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %492 = trunc i64 %489 to i32
  %493 = getelementptr inbounds nuw i8, ptr %37, i64 1620
  store volatile i32 %492, ptr %493, align 4, !tbaa !77
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.43) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %492) #9
  %494 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %494, align 1, !tbaa !23
  %495 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %489, i64 noundef 0, ptr noundef nonnull %3) #9
  br label %496

496:                                              ; preds = %486, %132
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.44) #9
  %497 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %497, align 1, !tbaa !23
  %498 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #9
  %499 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %500 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %501 = add i32 %500, 1
  store volatile i32 %501, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %502 = trunc i64 %499 to i32
  %503 = getelementptr inbounds nuw i8, ptr %37, i64 1624
  store volatile i32 %502, ptr %503, align 8, !tbaa !78
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.45) #9
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %502) #9
  %504 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %504, align 1, !tbaa !23
  %505 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %499, i64 noundef 0, ptr noundef nonnull %3) #9
  br label %506

506:                                              ; preds = %496, %467, %458, %444, %430, %283, %269, %262, %176, %164, %153, %122
  store ptr %3, ptr %4, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.46) #9
  %507 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  %508 = icmp eq i32 %507, 0
  br i1 %508, label %509, label %510

509:                                              ; preds = %506
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.47) #9
  store volatile i32 0, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  br label %512

510:                                              ; preds = %506
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.48) #9
  %511 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %511) #9
  br label %512

512:                                              ; preds = %510, %509
  %513 = load ptr, ptr %4, align 8, !tbaa !34
  store i8 0, ptr %513, align 1, !tbaa !23
  %514 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  %515 = zext i32 %514 to i64
  %516 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %517 = zext i32 %516 to i64
  %518 = call signext i32 @hddlog_write(i32 noundef zeroext 1162757152, i64 noundef %515, i64 noundef %517, ptr noundef nonnull %3) #9
  br label %519

519:                                              ; preds = %101, %512
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #10
  %520 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  %521 = or i32 %520, 2
  store volatile i32 %521, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !30
  br label %522

522:                                              ; preds = %519, %47
  %523 = getelementptr inbounds nuw i8, ptr %37, i64 1024
  %524 = zext nneg i32 %10 to i64
  %525 = getelementptr inbounds nuw [64 x i8], ptr %523, i64 %524
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #10
  store ptr %525, ptr %2, align 8, !tbaa !34
  switch i32 %10, label %592 [
    i32 0, label %526
    i32 1, label %542
    i32 2, label %550
    i32 3, label %557
    i32 4, label %571
    i32 5, label %577
    i32 6, label %584
    i32 7, label %587
  ]

526:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.84) #9
  %527 = getelementptr inbounds nuw i8, ptr %37, i64 2072
  %528 = load volatile i8, ptr %527, align 8, !tbaa !62
  %529 = icmp ult i8 %528, 7
  br i1 %529, label %530, label %534

530:                                              ; preds = %526
  %531 = zext nneg i8 %528 to i64
  %532 = getelementptr inbounds nuw [8 x i8], ptr @auth_verdict_to_str.STRS, i64 %531
  %533 = load ptr, ptr %532, align 8, !tbaa !34
  br label %534

534:                                              ; preds = %530, %526
  %535 = phi ptr [ %533, %530 ], [ @.str.61, %526 ]
  call fastcc void @append_str(ptr noundef %2, ptr noundef %535) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.85) #9
  %536 = getelementptr inbounds nuw i8, ptr %37, i64 2074
  %537 = load volatile i16, ptr %536, align 2, !tbaa !73
  %538 = zext i16 %537 to i32
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %538) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.86) #9
  %539 = getelementptr inbounds nuw i8, ptr %37, i64 2076
  %540 = load volatile i8, ptr %539, align 4, !tbaa !74
  %541 = zext i8 %540 to i32
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %541) #9
  br label %593

542:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.87) #9
  %543 = getelementptr inbounds nuw i8, ptr %37, i64 2144
  %544 = load volatile i16, ptr %543, align 8, !tbaa !64
  call fastcc void @format_hex16(ptr noundef %2, i16 noundef zeroext %544) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.88) #9
  %545 = getelementptr inbounds nuw i8, ptr %37, i64 2208
  %546 = load volatile i16, ptr %545, align 8, !tbaa !65
  call fastcc void @format_hex16(ptr noundef %2, i16 noundef zeroext %546) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.89) #9
  %547 = getelementptr inbounds nuw i8, ptr %37, i64 2152
  %548 = load volatile i64, ptr %547, align 8, !tbaa !79
  %549 = trunc i64 %548 to i32
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %549) #9
  br label %593

550:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.90) #9
  %551 = getelementptr inbounds nuw i8, ptr %37, i64 2096
  %552 = load volatile i32, ptr %551, align 8, !tbaa !69
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %552) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.91) #9
  %553 = getelementptr inbounds nuw i8, ptr %37, i64 2100
  %554 = load volatile i32, ptr %553, align 4, !tbaa !70
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %554) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.92) #9
  %555 = getelementptr inbounds nuw i8, ptr %37, i64 2088
  %556 = load volatile i32, ptr %555, align 8, !tbaa !67
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %556) #9
  br label %593

557:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.93) #9
  %558 = getelementptr inbounds nuw i8, ptr %37, i64 1736
  %559 = load volatile i8, ptr %558, align 8, !tbaa !80
  %560 = icmp ult i8 %559, 4
  br i1 %560, label %561, label %565

561:                                              ; preds = %557
  %562 = zext nneg i8 %559 to i64
  %563 = getelementptr inbounds nuw [8 x i8], ptr @class_to_str.STRS, i64 %562
  %564 = load ptr, ptr %563, align 8, !tbaa !34
  br label %565

565:                                              ; preds = %561, %557
  %566 = phi ptr [ %564, %561 ], [ @.str.82, %557 ]
  call fastcc void @append_str(ptr noundef %2, ptr noundef %566) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.94) #9
  %567 = getelementptr inbounds nuw i8, ptr %37, i64 1720
  %568 = load volatile i32, ptr %567, align 8, !tbaa !81
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %568) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.91) #9
  %569 = getelementptr inbounds nuw i8, ptr %37, i64 1692
  %570 = load volatile i32, ptr %569, align 4, !tbaa !82
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %570) #9
  br label %593

571:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.95) #9
  %572 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %572) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.96) #9
  %573 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !28
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %573) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.97) #9
  %574 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %575 = zext i16 %574 to i32
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %575) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.98) #9
  %576 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !83
  call fastcc void @format_hex32(ptr noundef %2, i32 noundef zeroext %576) #9
  br label %593

577:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.99) #9
  %578 = getelementptr inbounds nuw i8, ptr %37, i64 1720
  %579 = load volatile i32, ptr %578, align 8, !tbaa !81
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %579) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.100) #9
  %580 = getelementptr inbounds nuw i8, ptr %37, i64 1724
  %581 = load volatile i32, ptr %580, align 4, !tbaa !84
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %581) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.101) #9
  %582 = getelementptr inbounds nuw i8, ptr %37, i64 1728
  %583 = load volatile i32, ptr %582, align 8, !tbaa !85
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %583) #9
  br label %593

584:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.102) #9
  %585 = getelementptr inbounds nuw i8, ptr %37, i64 1760
  %586 = load volatile i64, ptr %585, align 8, !tbaa !44
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %586) #9
  br label %593

587:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.103) #9
  %588 = getelementptr inbounds nuw i8, ptr %37, i64 1744
  %589 = load volatile i64, ptr %588, align 8, !tbaa !51
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %589) #9
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.104) #9
  %590 = getelementptr inbounds nuw i8, ptr %37, i64 1752
  %591 = load volatile i64, ptr %590, align 8, !tbaa !53
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %591) #9
  br label %593

592:                                              ; preds = %522
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.105) #9
  br label %593

593:                                              ; preds = %534, %542, %550, %565, %571, %577, %584, %587, %592
  %594 = load ptr, ptr %2, align 8, !tbaa !34
  store i8 0, ptr %594, align 1, !tbaa !23
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #10
  br label %595

595:                                              ; preds = %33, %13, %593
  %596 = phi ptr [ %525, %593 ], [ inttoptr (i64 3165888 to ptr), %33 ], [ inttoptr (i64 3165888 to ptr), %13 ]
  ret ptr %596
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc ptr @get_arena() unnamed_addr #3 {
  %1 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %2 = tail call fastcc signext i32 @arena_rw(i64 noundef %1) #9
  %3 = icmp eq i32 %2, 0
  %4 = inttoptr i64 %1 to ptr
  %5 = select i1 %3, ptr null, ptr %4
  ret ptr %5
}

; Function Attrs: minsize optsize
declare i64 @native_alloc(i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc signext range(i32 0, 2) i32 @arena_rw(i64 noundef %0) unnamed_addr #3 {
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
define internal fastcc void @append_str(ptr nofree noundef nonnull captures(none) %0, ptr nofree noundef readonly captures(none) %1) unnamed_addr #4 {
  br label %3

3:                                                ; preds = %7, %2
  %4 = phi ptr [ %1, %2 ], [ %8, %7 ]
  %5 = load i8, ptr %4, align 1, !tbaa !23
  %6 = icmp eq i8 %5, 0
  br i1 %6, label %11, label %7

7:                                                ; preds = %3
  %8 = getelementptr inbounds nuw i8, ptr %4, i64 1
  %9 = load ptr, ptr %0, align 8, !tbaa !34
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 1
  store ptr %10, ptr %0, align 8, !tbaa !34
  store i8 %5, ptr %9, align 1, !tbaa !23
  br label %3, !llvm.loop !86

11:                                               ; preds = %3
  ret void
}

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_dec(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #4 {
  %3 = alloca [12 x i8], align 1
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #10
  %4 = icmp eq i32 %1, 0
  br i1 %4, label %5, label %8

5:                                                ; preds = %2
  %6 = load ptr, ptr %0, align 8, !tbaa !34
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 1
  store ptr %7, ptr %0, align 8, !tbaa !34
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
  br label %8, !llvm.loop !87

21:                                               ; preds = %8, %24
  %22 = phi i64 [ %25, %24 ], [ %9, %8 ]
  %23 = icmp sgt i64 %22, 0
  br i1 %23, label %24, label %30

24:                                               ; preds = %21
  %25 = add nsw i64 %22, -1
  %26 = getelementptr inbounds nuw i8, ptr %3, i64 %25
  %27 = load i8, ptr %26, align 1, !tbaa !23
  %28 = load ptr, ptr %0, align 8, !tbaa !34
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 1
  store ptr %29, ptr %0, align 8, !tbaa !34
  store i8 %27, ptr %28, align 1, !tbaa !23
  br label %21, !llvm.loop !88

30:                                               ; preds = %21, %5
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #10
  ret void
}

; Function Attrs: minsize optsize
declare i64 @lv1_hcall(i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex64(ptr nofree noundef nonnull captures(none) %0, i64 noundef %1) unnamed_addr #4 {
  tail call fastcc void @format_hex_n(ptr noundef %0, i64 noundef %1, i32 noundef signext 16) #9
  ret void
}

; Function Attrs: minsize noinline nounwind optsize
define internal fastcc signext range(i32 -1, 2) i32 @execute_atapi_cmd(i64 noundef range(i64 0, 8) %0, i8 noundef zeroext range(i8 -83, 71) %1, i32 noundef zeroext range(i32 0, 2049) %2, i32 noundef zeroext range(i32 0, 2) %3, i32 noundef zeroext range(i32 0, 2) %4, i32 noundef zeroext range(i32 5, 19) %5, i32 noundef zeroext range(i32 1, 1025) %6, ptr nofree noundef readonly captures(none) %7, ptr nofree noundef captures(address) %8, i64 noundef %9, ptr nofree noundef captures(address) %10, i64 noundef %11, ptr nofree noundef captures(address) %12, ptr nofree noundef captures(address) %13, ptr nofree noundef captures(address) %14, ptr nofree noundef captures(address) %15) unnamed_addr #5 {
  %17 = alloca [128 x i8], align 1
  %18 = alloca ptr, align 8
  tail call fastcc void @setup_atapi_block(ptr noundef %8, i8 noundef zeroext %1, i32 noundef zeroext %2, i32 noundef zeroext %3, i32 noundef zeroext %4, i64 noundef %11) #9
  %19 = icmp eq i32 %2, 0
  br i1 %19, label %21, label %20

20:                                               ; preds = %16
  tail call fastcc void @prefill_buffer(ptr noundef %10, i32 noundef zeroext %2, i8 noundef zeroext 0) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %17) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %18) #10
  store ptr %17, ptr %18, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.49) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.50) #9
  call fastcc void @format_hex64(ptr noundef %18, i64 noundef %9) #9
  br label %22

21:                                               ; preds = %16
  call void @llvm.lifetime.start.p0(ptr nonnull %17) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %18) #10
  store ptr %17, ptr %18, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.49) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef %7) #9
  br label %22

22:                                               ; preds = %21, %20
  %23 = phi ptr [ @.str.50, %21 ], [ @.str.51, %20 ]
  %24 = phi i64 [ %9, %21 ], [ %11, %20 ]
  %25 = phi i64 [ 0, %21 ], [ %11, %20 ]
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull %23) #9
  call fastcc void @format_hex64(ptr noundef %18, i64 noundef %24) #9
  %26 = load ptr, ptr %18, align 8, !tbaa !34
  store i8 0, ptr %26, align 1, !tbaa !23
  %27 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %9, i64 noundef %25, ptr noundef nonnull %17) #9
  %28 = zext nneg i32 %2 to i64
  %29 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %0, i64 noundef 1, i64 noundef %9, i64 noundef 64, i64 noundef %25, i64 noundef %28) #8
  %30 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %31 = add i32 %30, 1
  store volatile i32 %31, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %32 = trunc i64 %29 to i32
  store volatile i32 %32, ptr %12, align 4, !tbaa !20
  %33 = icmp eq i64 %29, 0
  br i1 %33, label %45, label %34

34:                                               ; preds = %22
  %35 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  %36 = icmp eq i32 %35, 0
  br i1 %36, label %37, label %38

37:                                               ; preds = %34
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  br label %38

38:                                               ; preds = %37, %34
  %39 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  %40 = icmp eq i32 %39, 0
  br i1 %40, label %41, label %42

41:                                               ; preds = %38
  store volatile i32 %32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  br label %42

42:                                               ; preds = %41, %38
  store ptr %17, ptr %18, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.52) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.53) #9
  call fastcc void @format_s32(ptr noundef %18, i32 noundef signext %32) #9
  %43 = load ptr, ptr %18, align 8, !tbaa !34
  store i8 0, ptr %43, align 1, !tbaa !23
  %44 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %29, i64 noundef 0, ptr noundef nonnull %17) #9
  br label %67

45:                                               ; preds = %22
  %46 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %47 = call fastcc signext i32 @poll_completion(i64 noundef %0, i64 noundef %46, ptr noundef %13, ptr noundef %14, ptr noundef %15) #9
  %48 = icmp eq i32 %47, 0
  br i1 %48, label %61, label %49

49:                                               ; preds = %45
  %50 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !83
  %51 = or i32 %50, %6
  store volatile i32 %51, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !83
  %52 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  %53 = icmp eq i32 %52, 0
  br i1 %53, label %54, label %55

54:                                               ; preds = %49
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  br label %55

55:                                               ; preds = %54, %49
  store ptr %17, ptr %18, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.54) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.55) #9
  %56 = load ptr, ptr %18, align 8, !tbaa !34
  store i8 0, ptr %56, align 1, !tbaa !23
  %57 = load volatile i32, ptr %14, align 4, !tbaa !20
  %58 = zext i32 %57 to i64
  %59 = load volatile i64, ptr %15, align 8, !tbaa !19
  %60 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %58, i64 noundef %59, ptr noundef nonnull %17) #9
  br label %67

61:                                               ; preds = %45
  store ptr %17, ptr %18, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.52) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.56) #9
  %62 = load volatile i64, ptr %13, align 8, !tbaa !19
  call fastcc void @format_hex64(ptr noundef %18, i64 noundef %62) #9
  call fastcc void @append_str(ptr noundef %18, ptr noundef nonnull @.str.31) #9
  %63 = load volatile i32, ptr %14, align 4, !tbaa !20
  call fastcc void @format_dec(ptr noundef %18, i32 noundef zeroext %63) #9
  %64 = load ptr, ptr %18, align 8, !tbaa !34
  store i8 0, ptr %64, align 1, !tbaa !23
  %65 = load volatile i64, ptr %13, align 8, !tbaa !19
  %66 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef 0, i64 noundef %65, ptr noundef nonnull %17) #9
  br label %67

67:                                               ; preds = %55, %61, %42
  %68 = phi i32 [ -1, %42 ], [ 1, %55 ], [ 0, %61 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %18) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %17) #10
  ret i32 %68
}

; Function Attrs: minsize nounwind optsize
define internal fastcc void @query_vuart_param(i64 noundef range(i64 2, 11) %0, i64 noundef range(i64 0, 4) %1, ptr nofree noundef captures(address) %2, ptr nofree noundef captures(address) %3, ptr nofree noundef readonly captures(none) %4) unnamed_addr #0 {
  %6 = alloca [64 x i8], align 1
  %7 = alloca ptr, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #10
  store ptr %6, ptr %7, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.57) #9
  call fastcc void @append_str(ptr noundef %7, ptr noundef %4) #9
  %8 = load ptr, ptr %7, align 8, !tbaa !34
  store i8 0, ptr %8, align 1, !tbaa !23
  %9 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %0, i64 noundef %1, ptr noundef nonnull %6) #9
  %10 = call i64 @lv1_hcall(i64 noundef 165, i64 noundef %0, i64 noundef %1, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %11 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %12 = add i32 %11, 1
  store volatile i32 %12, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %13 = trunc i64 %10 to i32
  store volatile i32 %13, ptr %2, align 4, !tbaa !20
  %14 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  store volatile i64 %14, ptr %3, align 8, !tbaa !19
  store ptr %6, ptr %7, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.58) #9
  call fastcc void @append_str(ptr noundef %7, ptr noundef %4) #9
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.59) #9
  call fastcc void @format_s32(ptr noundef %7, i32 noundef signext %13) #9
  call fastcc void @append_str(ptr noundef %7, ptr noundef nonnull @.str.60) #9
  %15 = load volatile i64, ptr %3, align 8, !tbaa !19
  call fastcc void @format_hex64(ptr noundef %7, i64 noundef %15) #9
  %16 = load ptr, ptr %7, align 8, !tbaa !34
  store i8 0, ptr %16, align 1, !tbaa !23
  %17 = load volatile i64, ptr %3, align 8, !tbaa !19
  %18 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %10, i64 noundef %17, ptr noundef nonnull %6) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #10
  ret void
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @format_auth_request(ptr nofree noundef captures(address) %0) unnamed_addr #6 {
  tail call fastcc void @prefill_buffer(ptr noundef %0, i32 noundef zeroext 112, i8 noundef zeroext 0) #9
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
define internal fastcc void @format_s32(ptr nofree noundef nonnull captures(none) %0, i32 noundef signext %1) unnamed_addr #4 {
  %3 = icmp slt i32 %1, 0
  br i1 %3, label %4, label %8

4:                                                ; preds = %2
  %5 = load ptr, ptr %0, align 8, !tbaa !34
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 1
  store ptr %6, ptr %0, align 8, !tbaa !34
  store i8 45, ptr %5, align 1, !tbaa !23
  %7 = sub nsw i32 0, %1
  br label %8

8:                                                ; preds = %2, %4
  %9 = phi i32 [ %7, %4 ], [ %1, %2 ]
  tail call fastcc void @format_dec(ptr noundef %0, i32 noundef zeroext %9) #9
  ret void
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @prefill_buffer(ptr nofree noundef captures(address) %0, i32 noundef zeroext range(i32 1, 2049) %1, i8 noundef zeroext range(i8 -91, 1) %2) unnamed_addr #6 {
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
  br label %5, !llvm.loop !89
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex32(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #4 {
  %3 = zext i32 %1 to i64
  tail call fastcc void @format_hex_n(ptr noundef %0, i64 noundef %3, i32 noundef signext 8) #9
  ret void
}

; Function Attrs: minsize noinline nounwind optsize
define internal fastcc signext range(i32 -1, 2) i32 @execute_read_test(i64 noundef range(i64 0, 8) %0, i32 noundef zeroext range(i32 0, 18) %1, i32 noundef zeroext range(i32 1, 2049) %2, i32 noundef zeroext range(i32 1, 2049) %3, i32 noundef zeroext range(i32 1, 4) %4, i32 noundef zeroext range(i32 8, 12) %5, i32 noundef zeroext range(i32 8, 65) %6, ptr nofree noundef readonly captures(none) %7, ptr nofree noundef captures(address) %8, i64 noundef %9, ptr nofree noundef captures(address) %10, i64 noundef %11, ptr nofree noundef captures(address) %12, ptr nofree noundef captures(address) %13, ptr nofree noundef captures(address) %14, ptr nofree noundef captures(address) %15, ptr nofree noundef captures(address) %16, ptr nofree noundef captures(address) %17, ptr nofree noundef captures(address) %18) unnamed_addr #5 {
  %20 = alloca [256 x i8], align 1
  %21 = alloca ptr, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %20) #10
  call void @llvm.lifetime.start.p0(ptr nonnull %21) #10
  tail call fastcc void @prefill_buffer(ptr noundef %10, i32 noundef zeroext 2048, i8 noundef zeroext -91) #9
  tail call fastcc void @prefill_buffer(ptr noundef %8, i32 noundef zeroext 64, i8 noundef zeroext 0) #9
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
  store ptr %20, ptr %21, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.49) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.68) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %1) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.69) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %4) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.70) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %2) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.71) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %3) #9
  %34 = load ptr, ptr %21, align 8, !tbaa !34
  store i8 0, ptr %34, align 1, !tbaa !23
  %35 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %9, i64 noundef %11, ptr noundef nonnull %20) #9
  %36 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef %0, i64 noundef 1, i64 noundef %9, i64 noundef 64, i64 noundef %11, i64 noundef 2048) #8
  %37 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %38 = add i32 %37, 1
  store volatile i32 %38, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %39 = trunc i64 %36 to i32
  store volatile i32 %39, ptr %13, align 4, !tbaa !20
  %40 = icmp eq i64 %36, 0
  br i1 %40, label %41, label %53

41:                                               ; preds = %19
  %42 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  %43 = call fastcc signext i32 @poll_completion(i64 noundef %0, i64 noundef %42, ptr noundef %14, ptr noundef %15, ptr noundef %16) #9
  %44 = icmp eq i32 %43, 0
  br i1 %44, label %61, label %45

45:                                               ; preds = %41
  %46 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !83
  %47 = or i32 %46, %6
  store volatile i32 %47, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !83
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  store ptr %20, ptr %21, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.54) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.55) #9
  %48 = load ptr, ptr %21, align 8, !tbaa !34
  store i8 0, ptr %48, align 1, !tbaa !23
  %49 = load volatile i32, ptr %15, align 4, !tbaa !20
  %50 = zext i32 %49 to i64
  %51 = load volatile i64, ptr %16, align 8, !tbaa !19
  %52 = call signext i32 @hddlog_write(i32 noundef zeroext 1414352672, i64 noundef %50, i64 noundef %51, ptr noundef nonnull %20) #9
  br label %141

53:                                               ; preds = %19
  %54 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  %55 = icmp eq i32 %54, 0
  br i1 %55, label %56, label %57

56:                                               ; preds = %53
  store volatile i32 %5, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !42
  br label %57

57:                                               ; preds = %56, %53
  %58 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
  %59 = icmp eq i32 %58, 0
  br i1 %59, label %60, label %61

60:                                               ; preds = %57
  store volatile i32 %39, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !43
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
  br label %62, !llvm.loop !90

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
  br label %96, !llvm.loop !91

110:                                              ; preds = %73, %91, %100
  %111 = phi i8 [ %102, %100 ], [ 0, %73 ], [ 2, %91 ]
  store volatile i8 %111, ptr %18, align 1, !tbaa !23
  store ptr %20, ptr %21, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.52) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef %7) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.59) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %39) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.72) #9
  %112 = load volatile i64, ptr %14, align 8, !tbaa !19
  call fastcc void @format_hex64(ptr noundef %21, i64 noundef %112) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.73) #9
  %113 = zext nneg i8 %111 to i64
  %114 = getelementptr inbounds nuw [8 x i8], ptr @class_to_str.STRS, i64 %113
  %115 = load ptr, ptr %114, align 8, !tbaa !34
  call fastcc void @append_str(ptr noundef %21, ptr noundef %115) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.74) #9
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %64) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.31) #9
  %116 = load volatile i32, ptr %15, align 4, !tbaa !20
  call fastcc void @format_dec(ptr noundef %21, i32 noundef zeroext %116) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.75) #9
  call fastcc void @format_bytes_hex(ptr noundef %21, ptr noundef %10) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.76) #9
  %117 = getelementptr inbounds nuw i8, ptr %10, i64 16
  call fastcc void @format_bytes_hex(ptr noundef %21, ptr noundef nonnull %117) #9
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.77) #9
  %118 = getelementptr inbounds nuw i8, ptr %10, i64 40
  %119 = load ptr, ptr %21, align 8
  br label %120

120:                                              ; preds = %124, %110
  %121 = phi ptr [ %129, %124 ], [ %119, %110 ]
  %122 = phi i64 [ %131, %124 ], [ 0, %110 ]
  %123 = icmp eq i64 %122, 8
  br i1 %123, label %132, label %124

124:                                              ; preds = %120
  %125 = getelementptr inbounds nuw i8, ptr %118, i64 %122
  %126 = load volatile i8, ptr %125, align 1, !tbaa !23
  %127 = add i8 %126, -32
  %128 = icmp ult i8 %127, 95
  %129 = getelementptr inbounds nuw i8, ptr %121, i64 1
  %130 = select i1 %128, i8 %126, i8 46
  store i8 %130, ptr %121, align 1, !tbaa !23
  %131 = add nuw nsw i64 %122, 1
  br label %120, !llvm.loop !92

132:                                              ; preds = %120
  store ptr %121, ptr %21, align 8
  call fastcc void @append_str(ptr noundef %21, ptr noundef nonnull @.str.78) #9
  %133 = load ptr, ptr %21, align 8, !tbaa !34
  store i8 0, ptr %133, align 1, !tbaa !23
  %134 = load volatile i64, ptr %14, align 8, !tbaa !19
  %135 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %36, i64 noundef %134, ptr noundef nonnull %20) #9
  br i1 %40, label %136, label %140

136:                                              ; preds = %132
  %137 = load volatile i64, ptr %14, align 8, !tbaa !19
  %138 = and i64 %137, 255
  %139 = icmp eq i64 %138, 2
  br i1 %139, label %140, label %141

140:                                              ; preds = %136, %132
  call fastcc void @do_request_sense(i64 noundef %0, ptr noundef nonnull %8, i64 noundef %9, ptr noundef nonnull %10, i64 noundef %11, ptr noundef %12) #9
  br label %141

141:                                              ; preds = %45, %140, %136
  %142 = phi i32 [ 1, %45 ], [ -1, %140 ], [ 0, %136 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %21) #10
  call void @llvm.lifetime.end.p0(ptr nonnull %20) #10
  ret i32 %142
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex_n(ptr nofree noundef nonnull captures(none) %0, i64 noundef %1, i32 noundef signext range(i32 4, 17) %2) unnamed_addr #4 {
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
  %16 = load ptr, ptr %0, align 8, !tbaa !34
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 1
  store ptr %17, ptr %0, align 8, !tbaa !34
  store i8 %15, ptr %16, align 1, !tbaa !23
  br label %6, !llvm.loop !93
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @setup_atapi_block(ptr nofree noundef captures(address) %0, i8 noundef zeroext range(i8 -83, 71) %1, i32 noundef zeroext range(i32 0, 2049) %2, i32 noundef zeroext range(i32 0, 2) %3, i32 noundef zeroext range(i32 0, 2) %4, i64 noundef %5) unnamed_addr #6 {
  tail call fastcc void @prefill_buffer(ptr noundef %0, i32 noundef zeroext 64, i8 noundef zeroext 0) #9
  store volatile i8 %1, ptr %0, align 1, !tbaa !23
  switch i8 %1, label %23 [
    i8 18, label %19
    i8 3, label %19
    i8 70, label %10
    i8 -83, label %7
  ]

7:                                                ; preds = %6
  %8 = getelementptr inbounds nuw i8, ptr %0, i64 1
  store volatile i8 0, ptr %8, align 1, !tbaa !23
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 6
  store volatile i8 0, ptr %9, align 1, !tbaa !23
  br label %10

10:                                               ; preds = %6, %7
  %11 = phi i64 [ 7, %7 ], [ 1, %6 ]
  %12 = phi i8 [ 0, %7 ], [ 2, %6 ]
  %13 = phi i64 [ 8, %7 ], [ 7, %6 ]
  %14 = phi i64 [ 9, %7 ], [ 8, %6 ]
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 %11
  store volatile i8 %12, ptr %15, align 1, !tbaa !23
  %16 = lshr i32 %2, 8
  %17 = trunc nuw nsw i32 %16 to i8
  %18 = getelementptr inbounds nuw i8, ptr %0, i64 %13
  store volatile i8 %17, ptr %18, align 1, !tbaa !23
  br label %19

19:                                               ; preds = %10, %6, %6
  %20 = phi i64 [ 4, %6 ], [ 4, %6 ], [ %14, %10 ]
  %21 = trunc i32 %2 to i8
  %22 = getelementptr inbounds nuw i8, ptr %0, i64 %20
  store volatile i8 %21, ptr %22, align 1, !tbaa !23
  br label %23

23:                                               ; preds = %19, %6
  %24 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store volatile i32 12, ptr %24, align 4, !tbaa !20
  %25 = getelementptr inbounds nuw i8, ptr %0, i64 36
  store volatile i32 %2, ptr %25, align 4, !tbaa !20
  %26 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store volatile i32 1, ptr %26, align 4, !tbaa !20
  %27 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store volatile i32 %3, ptr %27, align 4, !tbaa !20
  %28 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store volatile i32 %4, ptr %28, align 4, !tbaa !20
  %29 = getelementptr inbounds nuw i8, ptr %0, i64 56
  store volatile i64 %5, ptr %29, align 8, !tbaa !19
  ret void
}

; Function Attrs: minsize nounwind optsize
define internal fastcc signext range(i32 0, 2) i32 @poll_completion(i64 noundef range(i64 0, 8) %0, i64 noundef %1, ptr nofree noundef captures(address) %2, ptr nofree noundef captures(address) %3, ptr nofree noundef captures(address) %4) unnamed_addr #0 {
  %6 = tail call i64 @native_clock() #8
  br label %7

7:                                                ; preds = %19, %5
  %8 = phi i32 [ 0, %5 ], [ %20, %19 ]
  %9 = icmp eq i32 %8, 200000
  br i1 %9, label %24, label %10

10:                                               ; preds = %7
  %11 = tail call i64 @lv1_hcall(i64 noundef 254, i64 noundef %0, i64 noundef %1, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #8
  %12 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %13 = add i32 %12, 1
  store volatile i32 %13, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !47
  %14 = icmp eq i64 %11, 0
  br i1 %14, label %21, label %15

15:                                               ; preds = %10
  %16 = tail call i64 @native_clock() #8
  %17 = sub i64 %16, %6
  %18 = icmp ugt i64 %17, 159999999
  br i1 %18, label %24, label %19

19:                                               ; preds = %15
  %20 = add nuw nsw i32 %8, 1
  br label %7, !llvm.loop !94

21:                                               ; preds = %10
  %22 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !50
  store volatile i64 %22, ptr %2, align 8, !tbaa !19
  %23 = add nuw nsw i32 %8, 1
  store volatile i32 %23, ptr %3, align 4, !tbaa !20
  br label %24

24:                                               ; preds = %7, %15, %21
  %25 = phi i32 [ 0, %21 ], [ 1, %15 ], [ 1, %7 ]
  %26 = tail call i64 @native_clock() #8
  %27 = sub i64 %26, %6
  store volatile i64 %27, ptr %4, align 8, !tbaa !19
  ret i32 %25
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
  %14 = load ptr, ptr %0, align 8, !tbaa !34
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 1
  store ptr %15, ptr %0, align 8, !tbaa !34
  store i8 %13, ptr %14, align 1, !tbaa !23
  %16 = load volatile i8, ptr %8, align 1, !tbaa !23
  %17 = and i8 %16, 15
  %18 = zext nneg i8 %17 to i64
  %19 = getelementptr inbounds nuw i8, ptr @HEX_DIGITS, i64 %18
  %20 = load i8, ptr %19, align 1, !tbaa !23
  %21 = load ptr, ptr %0, align 8, !tbaa !34
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 1
  store ptr %22, ptr %0, align 8, !tbaa !34
  store i8 %20, ptr %21, align 1, !tbaa !23
  %23 = add nuw nsw i64 %4, 1
  br label %3, !llvm.loop !95
}

; Function Attrs: minsize noinline nounwind optsize
define internal fastcc void @do_request_sense(i64 noundef range(i64 0, 8) %0, ptr nofree noundef captures(address) %1, i64 noundef %2, ptr nofree noundef captures(address) %3, i64 noundef %4, ptr nofree noundef captures(address) %5) unnamed_addr #5 {
  %7 = getelementptr inbounds nuw i8, ptr %5, i64 1656
  %8 = getelementptr inbounds nuw i8, ptr %5, i64 1848
  %9 = getelementptr inbounds nuw i8, ptr %5, i64 1708
  %10 = getelementptr inbounds nuw i8, ptr %5, i64 1912
  %11 = tail call fastcc signext i32 @execute_atapi_cmd(i64 noundef %0, i8 noundef zeroext 3, i32 noundef zeroext 18, i32 noundef zeroext 1, i32 noundef zeroext 1, i32 noundef zeroext 12, i32 noundef zeroext 128, ptr noundef nonnull @.str.83, ptr noundef %1, i64 noundef %2, ptr noundef %3, i64 noundef %4, ptr noundef nonnull %7, ptr noundef nonnull %8, ptr noundef nonnull %9, ptr noundef nonnull %10) #9
  %12 = getelementptr inbounds nuw i8, ptr %5, i64 1956
  br label %13

13:                                               ; preds = %17, %6
  %14 = phi i64 [ %21, %17 ], [ 0, %6 ]
  %15 = icmp eq i64 %14, 18
  br i1 %15, label %16, label %17

16:                                               ; preds = %13
  ret void

17:                                               ; preds = %13
  %18 = getelementptr inbounds nuw i8, ptr %3, i64 %14
  %19 = load volatile i8, ptr %18, align 1, !tbaa !23
  %20 = getelementptr inbounds nuw i8, ptr %12, i64 %14
  store volatile i8 %19, ptr %20, align 1, !tbaa !23
  %21 = add nuw nsw i64 %14, 1
  br label %13, !llvm.loop !96
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex16(ptr nofree noundef nonnull captures(none) %0, i16 noundef zeroext %1) unnamed_addr #4 {
  %3 = zext i16 %1 to i64
  tail call fastcc void @format_hex_n(ptr noundef %0, i64 noundef %3, i32 noundef signext 4) #9
  ret void
}

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #3 = { minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #4 = { minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #5 = { minsize noinline nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #6 = { minsize nofree noinline norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #7 = { minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #8 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #9 = { minsize nobuiltin optsize "no-builtins" }
attributes #10 = { nounwind }

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
!13 = !{!"ProbeArena", !6, i64 0, !6, i64 512, !6, i64 1024, !5, i64 1600, !5, i64 1604, !5, i64 1608, !5, i64 1612, !5, i64 1616, !5, i64 1620, !5, i64 1624, !5, i64 1628, !5, i64 1632, !5, i64 1636, !5, i64 1640, !5, i64 1644, !5, i64 1648, !5, i64 1652, !5, i64 1656, !5, i64 1660, !5, i64 1664, !5, i64 1668, !5, i64 1672, !5, i64 1676, !5, i64 1680, !5, i64 1684, !5, i64 1688, !5, i64 1692, !5, i64 1696, !5, i64 1700, !5, i64 1704, !5, i64 1708, !5, i64 1712, !5, i64 1716, !5, i64 1720, !5, i64 1724, !5, i64 1728, !5, i64 1732, !6, i64 1736, !6, i64 1737, !6, i64 1738, !6, i64 1739, !10, i64 1744, !10, i64 1752, !10, i64 1760, !10, i64 1768, !10, i64 1776, !10, i64 1784, !10, i64 1792, !10, i64 1800, !10, i64 1808, !10, i64 1816, !10, i64 1824, !10, i64 1832, !10, i64 1840, !10, i64 1848, !10, i64 1856, !10, i64 1864, !10, i64 1872, !10, i64 1880, !10, i64 1888, !10, i64 1896, !10, i64 1904, !10, i64 1912, !6, i64 1920, !6, i64 1956, !6, i64 1974, !5, i64 2008, !5, i64 2012, !5, i64 2016, !5, i64 2020, !5, i64 2024, !10, i64 2032, !10, i64 2040, !10, i64 2048, !10, i64 2056, !10, i64 2064, !6, i64 2072, !6, i64 2073, !11, i64 2074, !6, i64 2076, !6, i64 2077, !5, i64 2080, !5, i64 2084, !5, i64 2088, !5, i64 2092, !5, i64 2096, !5, i64 2100, !10, i64 2104, !5, i64 2112, !10, i64 2120, !5, i64 2128, !10, i64 2136, !11, i64 2144, !5, i64 2148, !10, i64 2152, !5, i64 2160, !10, i64 2168, !5, i64 2176, !10, i64 2184, !5, i64 2192, !10, i64 2200, !11, i64 2208}
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
!26 = distinct !{!26, !22}
!27 = distinct !{!27, !22}
!28 = !{!9, !5, i64 72}
!29 = !{!9, !6, i64 79}
!30 = !{!9, !5, i64 0}
!31 = distinct !{!31, !22}
!32 = !{!9, !10, i64 64}
!33 = !{!9, !5, i64 20}
!34 = !{!35, !35, i64 0}
!35 = !{!"p1 omnipotent char", !36, i64 0}
!36 = !{!"any pointer", !6, i64 0}
!37 = !{!13, !5, i64 1664}
!38 = !{!9, !5, i64 40}
!39 = !{!9, !5, i64 44}
!40 = !{!13, !5, i64 1660}
!41 = distinct !{!41, !22}
!42 = !{!9, !5, i64 12}
!43 = !{!9, !5, i64 16}
!44 = !{!13, !10, i64 1760}
!45 = !{!13, !10, i64 1768}
!46 = !{!13, !10, i64 1776}
!47 = !{!9, !5, i64 4}
!48 = !{!13, !5, i64 1604}
!49 = !{!13, !5, i64 1608}
!50 = !{!9, !10, i64 80}
!51 = !{!13, !10, i64 1744}
!52 = !{!13, !5, i64 1612}
!53 = !{!13, !10, i64 1752}
!54 = distinct !{!54, !22}
!55 = !{!13, !5, i64 1712}
!56 = !{!13, !5, i64 1716}
!57 = !{!13, !5, i64 2012}
!58 = !{!13, !5, i64 1628}
!59 = !{!13, !10, i64 1792}
!60 = !{!13, !5, i64 1636}
!61 = !{!13, !10, i64 1808}
!62 = !{!13, !6, i64 2072}
!63 = !{!13, !6, i64 2073}
!64 = !{!13, !11, i64 2144}
!65 = !{!13, !11, i64 2208}
!66 = !{!13, !5, i64 2084}
!67 = !{!13, !5, i64 2088}
!68 = !{!13, !5, i64 2092}
!69 = !{!13, !5, i64 2096}
!70 = !{!13, !5, i64 2100}
!71 = !{!13, !10, i64 2104}
!72 = !{!13, !5, i64 2080}
!73 = !{!13, !11, i64 2074}
!74 = !{!13, !6, i64 2076}
!75 = distinct !{!75, !22}
!76 = !{!13, !5, i64 1616}
!77 = !{!13, !5, i64 1620}
!78 = !{!13, !5, i64 1624}
!79 = !{!13, !10, i64 2152}
!80 = !{!13, !6, i64 1736}
!81 = !{!13, !5, i64 1720}
!82 = !{!13, !5, i64 1692}
!83 = !{!9, !5, i64 8}
!84 = !{!13, !5, i64 1724}
!85 = !{!13, !5, i64 1728}
!86 = distinct !{!86, !22}
!87 = distinct !{!87, !22}
!88 = distinct !{!88, !22}
!89 = distinct !{!89, !22}
!90 = distinct !{!90, !22}
!91 = distinct !{!91, !22}
!92 = distinct !{!92, !22}
!93 = distinct !{!93, !22}
!94 = distinct !{!94, !22}
!95 = distinct !{!95, !22}
!96 = distinct !{!96, !22}
