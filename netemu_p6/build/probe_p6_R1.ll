; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@hddlog_init.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@hddlog_write.path = internal constant [20 x i8] c"/tmp/netemu_log.bin\00", align 1
@.str = private unnamed_addr constant [23 x i8] c"boot: ps2_netemu_p6_r1\00", align 1
@.str.1 = private unnamed_addr constant [15 x i8] c"scan: rom_cnt=\00", align 1
@.str.2 = private unnamed_addr constant [6 x i8] c" hdd=\00", align 1
@.str.3 = private unnamed_addr constant [13 x i8] c" bus=4 dev=2\00", align 1
@.str.4 = private unnamed_addr constant [33 x i8] c"grd reject: sanity failed (0 hc)\00", align 1
@.str.5 = private unnamed_addr constant [39 x i8] c"finish: ps2_netemu_p6_r1 failed step=1\00", align 1
@.str.6 = private unnamed_addr constant [30 x i8] c"grd ok: lpar & ea sanity pass\00", align 1
@.str.7 = private unnamed_addr constant [22 x i8] c"pre open: bus=4 dev=2\00", align 1
@.str.8 = private unnamed_addr constant [15 x i8] c"post open: rc=\00", align 1
@.str.9 = private unnamed_addr constant [17 x i8] c"pre free: rgn=0x\00", align 1
@.str.10 = private unnamed_addr constant [15 x i8] c"post free: rc=\00", align 1
@.str.11 = private unnamed_addr constant [21 x i8] c"pre dma_alloc: sz=0x\00", align 1
@.str.12 = private unnamed_addr constant [7 x i8] c" pexp=\00", align 1
@.str.13 = private unnamed_addr constant [20 x i8] c"post dma_alloc: rc=\00", align 1
@.str.14 = private unnamed_addr constant [28 x i8] c"post dma_alloc: rc=0 rgn=0x\00", align 1
@.str.15 = private unnamed_addr constant [10 x i8] c"pre map #\00", align 1
@.str.16 = private unnamed_addr constant [10 x i8] c": lpar=0x\00", align 1
@.str.17 = private unnamed_addr constant [8 x i8] c" len=0x\00", align 1
@.str.18 = private unnamed_addr constant [8 x i8] c" flg=0x\00", align 1
@.str.19 = private unnamed_addr constant [11 x i8] c"post map #\00", align 1
@.str.20 = private unnamed_addr constant [6 x i8] c": rc=\00", align 1
@.str.21 = private unnamed_addr constant [13 x i8] c" bus_addr=0x\00", align 1
@.str.22 = private unnamed_addr constant [18 x i8] c"pre unmap: rgn=0x\00", align 1
@.str.23 = private unnamed_addr constant [16 x i8] c"post unmap: rc=\00", align 1
@.str.24 = private unnamed_addr constant [23 x i8] c"pre close: bus=4 dev=2\00", align 1
@.str.25 = private unnamed_addr constant [16 x i8] c"post close: rc=\00", align 1
@.str.26 = private unnamed_addr constant [26 x i8] c"finish: ps2_netemu_p6_r1 \00", align 1
@.str.27 = private unnamed_addr constant [7 x i8] c"cand #\00", align 1
@.str.28 = private unnamed_addr constant [5 x i8] c" ok!\00", align 1
@.str.29 = private unnamed_addr constant [32 x i8] c"all map candidates failed (-17)\00", align 1
@candidates = internal unnamed_addr constant [7 x { i8, i8, i8, i8, i32, i32, [4 x i8], i64 }] [{ i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 1, i8 0, i8 20, i8 0, i32 1048576, i32 1048576, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 2, i8 0, i8 16, i8 0, i32 1048576, i32 524288, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 3, i8 0, i8 12, i8 0, i32 524288, i32 524288, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 4, i8 1, i8 16, i8 0, i32 524288, i32 524288, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 5, i8 1, i8 12, i8 0, i32 524288, i32 524288, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 6, i8 2, i8 16, i8 0, i32 524288, i32 524288, [4 x i8] zeroinitializer, i64 -2305843009213691904 }, { i8, i8, i8, i8, i32, i32, [4 x i8], i64 } { i8 7, i8 3, i8 20, i8 0, i32 1048576, i32 1048576, [4 x i8] zeroinitializer, i64 -2305843009213691904 }], align 8
@__const.format_hex32.hex = private unnamed_addr constant [17 x i8] c"0123456789abcdef\00", align 1
@.str.31 = private unnamed_addr constant [6 x i8] c"P6-R1\00", align 1
@.str.32 = private unnamed_addr constant [22 x i8] c" SANITY REJECT (0 HC)\00", align 1
@.str.33 = private unnamed_addr constant [14 x i8] c" DONE: CAND #\00", align 1
@.str.34 = private unnamed_addr constant [8 x i8] c" MAP OK\00", align 1
@.str.35 = private unnamed_addr constant [37 x i8] c" FAIL: ALL CANDIDATES REJECTED (-17)\00", align 1
@.str.36 = private unnamed_addr constant [5 x i8] c"WIN=\00", align 1
@.str.37 = private unnamed_addr constant [9 x i8] c" TESTED=\00", align 1
@.str.38 = private unnamed_addr constant [5 x i8] c" HC=\00", align 1
@.str.39 = private unnamed_addr constant [6 x i8] c" LOG=\00", align 1
@.str.40 = private unnamed_addr constant [14 x i8] c"CDVD LPAR: 0x\00", align 1
@.str.41 = private unnamed_addr constant [14 x i8] c"CDVD EA:   0x\00", align 1
@.str.42 = private unnamed_addr constant [5 x i8] c" SZ=\00", align 1
@.str.43 = private unnamed_addr constant [11 x i8] c"DMA RGN=0x\00", align 1
@.str.44 = private unnamed_addr constant [8 x i8] c" BUS=0x\00", align 1
@.str.45 = private unnamed_addr constant [8 x i8] c"RC: OP=\00", align 1
@.str.46 = private unnamed_addr constant [8 x i8] c" ALLOC=\00", align 1
@.str.47 = private unnamed_addr constant [6 x i8] c" MAP=\00", align 1
@.str.48 = private unnamed_addr constant [5 x i8] c" CL=\00", align 1
@.str.49 = private unnamed_addr constant [11 x i8] c"SCAN: ROM=\00", align 1
@.str.50 = private unnamed_addr constant [6 x i8] c" HDD=\00", align 1
@.str.51 = private unnamed_addr constant [6 x i8] c" TOT=\00", align 1
@.str.52 = private unnamed_addr constant [14 x i8] c"P6-R1 RUNNING\00", align 1

; Function Attrs: minsize nounwind optsize
define dso_local signext range(i32 -1, 1) i32 @hddlog_init() local_unnamed_addr #0 {
  %1 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %2 = icmp eq i64 %1, 0
  br i1 %2, label %57, label %3

3:                                                ; preds = %0
  %4 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %5 = inttoptr i64 %4 to ptr
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 1644
  %7 = load volatile i32, ptr %6, align 4, !tbaa !12
  %8 = icmp eq i32 %7, 0
  br i1 %8, label %9, label %57

9:                                                ; preds = %3
  %10 = tail call i64 @native_clock() #6
  %11 = getelementptr inbounds nuw i8, ptr %5, i64 1696
  store volatile i64 %10, ptr %11, align 8, !tbaa !14
  %12 = getelementptr inbounds nuw i8, ptr %5, i64 1648
  store volatile i32 1, ptr %12, align 8, !tbaa !15
  %13 = getelementptr inbounds nuw i8, ptr %5, i64 1652
  store volatile i32 0, ptr %13, align 4, !tbaa !16
  %14 = tail call fastcc signext i32 @is_hdd_log_safe() #7
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
  %20 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_init.path) #6
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
  %39 = tail call i64 @stock_raw_write(i32 noundef signext %20, i64 noundef 0, ptr noundef nonnull %5, i64 noundef 512) #6
  %40 = icmp eq i64 %39, 512
  %41 = tail call signext i32 @stock_ufs_close(i32 noundef signext %20) #6
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
  %50 = tail call fastcc signext i32 @is_hdd_log_safe() #7
  %51 = icmp eq i32 %50, 0
  br i1 %51, label %56, label %52

52:                                               ; preds = %49
  %53 = tail call signext i32 @stock_hdd_cache_flush() #6
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
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 1644
  %11 = load volatile i32, ptr %10, align 4, !tbaa !12
  %12 = icmp eq i32 %11, 0
  br i1 %12, label %106, label %13

13:                                               ; preds = %7
  %14 = getelementptr inbounds nuw i8, ptr %9, i64 1648
  %15 = load volatile i32, ptr %14, align 8, !tbaa !15
  %16 = icmp ugt i32 %15, 127
  br i1 %16, label %17, label %18

17:                                               ; preds = %13
  store volatile i8 8, ptr inttoptr (i64 9637742 to ptr), align 2, !tbaa !17
  br label %106

18:                                               ; preds = %13
  %19 = tail call fastcc signext i32 @is_hdd_log_safe() #7
  %20 = icmp eq i32 %19, 0
  br i1 %20, label %21, label %24

21:                                               ; preds = %18
  %22 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %23 = add i16 %22, 1
  store volatile i16 %23, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  br label %106

24:                                               ; preds = %18
  %25 = tail call signext i32 @stock_ufs_open(i64 noundef 0, ptr noundef nonnull @hddlog_write.path) #6
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
  %36 = getelementptr inbounds nuw i8, ptr %9, i64 1652
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
  %43 = tail call i64 @native_clock() #6
  %44 = getelementptr inbounds nuw i8, ptr %9, i64 528
  store volatile i64 %43, ptr %44, align 8, !tbaa !19
  %45 = getelementptr inbounds nuw i8, ptr %9, i64 536
  store volatile i64 %1, ptr %45, align 8, !tbaa !19
  %46 = getelementptr inbounds nuw i8, ptr %9, i64 544
  store volatile i64 %2, ptr %46, align 8, !tbaa !19
  %47 = getelementptr inbounds nuw i8, ptr %9, i64 1696
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
  %68 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef %67, ptr noundef nonnull %31, i64 noundef 512) #6
  %69 = icmp eq i64 %68, 512
  br i1 %69, label %75, label %73

70:                                               ; preds = %32
  %71 = getelementptr inbounds nuw [8 x i8], ptr %31, i64 %33
  store volatile i64 0, ptr %71, align 8, !tbaa !19
  %72 = add nuw nsw i64 %33, 1
  br label %32, !llvm.loop !25

73:                                               ; preds = %62
  %74 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #6
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
  %86 = tail call i64 @stock_raw_write(i32 noundef signext %25, i64 noundef 0, ptr noundef nonnull %9, i64 noundef 512) #6
  %87 = icmp eq i64 %86, 512
  %88 = tail call signext i32 @stock_ufs_close(i32 noundef signext %25) #6
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
  %94 = tail call fastcc signext i32 @is_hdd_log_safe() #7
  %95 = icmp eq i32 %94, 0
  br i1 %95, label %96, label %99

96:                                               ; preds = %93
  %97 = load volatile i16, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  %98 = add i16 %97, 1
  store volatile i16 %98, ptr inttoptr (i64 9637740 to ptr), align 4, !tbaa !18
  br label %106

99:                                               ; preds = %93
  %100 = tail call signext i32 @stock_hdd_cache_flush() #6
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
  %3 = alloca [128 x i8], align 1
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = icmp ugt i32 %0, 8
  %10 = select i1 %9, i32 0, i32 %0
  %11 = tail call fastcc ptr @get_arena() #7
  %12 = icmp eq ptr %11, null
  br i1 %12, label %13, label %36

13:                                               ; preds = %1
  %14 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %15 = and i32 %14, 8
  %16 = icmp eq i32 %15, 0
  br i1 %16, label %17, label %329

17:                                               ; preds = %13
  %18 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %19 = or i32 %18, 1
  store volatile i32 %19, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %20 = tail call i64 @native_alloc(i64 noundef 4096, i64 noundef 3, i64 noundef 0) #6
  %21 = tail call fastcc signext i32 @arena_rw(i64 noundef %20) #7
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
  %29 = icmp eq i64 %28, 1704
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
  br label %329

36:                                               ; preds = %27, %1
  %37 = phi ptr [ %11, %1 ], [ %26, %27 ]
  %38 = tail call i64 @native_clock() #6
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
  br i1 %50, label %51, label %277

51:                                               ; preds = %47
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #8
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #8
  %52 = tail call signext i32 @hddlog_init() #7
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str) #7
  %53 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %53, align 1, !tbaa !23
  %54 = call signext i32 @hddlog_write(i32 noundef zeroext 1112493908, i64 noundef 1704, i64 noundef 1, ptr noundef nonnull %3) #7
  %55 = getelementptr inbounds nuw i8, ptr %37, i64 1628
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
  %64 = getelementptr inbounds nuw i8, ptr %37, i64 1632
  store volatile i32 %58, ptr %64, align 8, !tbaa !35
  store volatile i32 %61, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !36
  store volatile i32 %60, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !37
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.1) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %61) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.2) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %60) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.3) #7
  %65 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %65, align 1, !tbaa !23
  %66 = zext i32 %61 to i64
  %67 = zext nneg i32 %60 to i64
  %68 = call signext i32 @hddlog_write(i32 noundef zeroext 1396916558, i64 noundef %66, i64 noundef %67, ptr noundef nonnull %3) #7
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
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #8
  store i64 0, ptr %5, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #8
  store i64 0, ptr %6, align 8, !tbaa !19
  %80 = or disjoint i64 %57, 7234318118812647424
  %81 = call i64 @repo_read(ptr noundef nonnull %5, ptr noundef nonnull %6, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8392862959675637760, i64 noundef 0) #6
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
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #8
  store i64 0, ptr %7, align 8, !tbaa !19
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #8
  store i64 0, ptr %8, align 8, !tbaa !19
  %88 = call i64 @repo_read(ptr noundef nonnull %7, ptr noundef nonnull %8, i64 noundef 7094703231829278724, i64 noundef %80, i64 noundef 8243108395510267904, i64 noundef 0) #6
  %89 = icmp eq i64 %88, 0
  br i1 %89, label %90, label %93

90:                                               ; preds = %86
  %91 = load i64, ptr %7, align 8, !tbaa !19
  %92 = trunc i64 %91 to i32
  store volatile i32 %92, ptr %55, align 4, !tbaa !38
  br label %93

93:                                               ; preds = %90, %86
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #8
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #8
  br label %95

94:                                               ; preds = %83
  br label %95

95:                                               ; preds = %94, %93, %83, %79
  %96 = phi i32 [ %84, %93 ], [ %84, %94 ], [ %84, %83 ], [ %58, %79 ]
  %97 = phi i64 [ %57, %93 ], [ %59, %94 ], [ %59, %83 ], [ %59, %79 ]
  %98 = phi i32 [ %60, %93 ], [ 1, %94 ], [ %60, %83 ], [ %60, %79 ]
  %99 = phi i32 [ %87, %93 ], [ %61, %94 ], [ %61, %83 ], [ %61, %79 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #8
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #8
  %100 = add nuw nsw i64 %57, 1
  br label %56, !llvm.loop !39

101:                                              ; preds = %63
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 -1, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.4) #7
  %102 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %102, align 1, !tbaa !23
  %103 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #7
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.5) #7
  %104 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %104, align 1, !tbaa !23
  %105 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  br label %269

106:                                              ; preds = %63
  %107 = getelementptr inbounds nuw i8, ptr %37, i64 1672
  store volatile i64 %69, ptr %107, align 8, !tbaa !42
  %108 = getelementptr inbounds nuw i8, ptr %37, i64 1680
  store volatile i64 %70, ptr %108, align 8, !tbaa !43
  %109 = getelementptr inbounds nuw i8, ptr %37, i64 1688
  store volatile i64 %71, ptr %109, align 8, !tbaa !44
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.6) #7
  %110 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %110, align 1, !tbaa !23
  %111 = call signext i32 @hddlog_write(i32 noundef zeroext 1196573728, i64 noundef %69, i64 noundef %70, ptr noundef nonnull %3) #7
  %112 = load volatile i64, ptr inttoptr (i64 37865568 to ptr), align 32, !tbaa !19
  %113 = icmp eq i64 %112, 3
  br i1 %113, label %114, label %121

114:                                              ; preds = %106
  %115 = load volatile i64, ptr inttoptr (i64 37865584 to ptr), align 16, !tbaa !19
  %116 = load volatile i64, ptr inttoptr (i64 37865592 to ptr), align 8, !tbaa !19
  %117 = and i64 %115, 281470682791935
  %118 = icmp eq i64 %117, 87960930222080
  %119 = select i1 %118, i64 %116, i64 0
  %120 = select i1 %118, i64 %115, i64 0
  br label %121

121:                                              ; preds = %114, %106
  %122 = phi i64 [ 0, %106 ], [ %119, %114 ]
  %123 = phi i64 [ 0, %106 ], [ %120, %114 ]
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.7) #7
  %124 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %124, align 1, !tbaa !23
  %125 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #7
  %126 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %127 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %128 = add i32 %127, 1
  store volatile i32 %128, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %129 = trunc i64 %126 to i32
  %130 = getelementptr inbounds nuw i8, ptr %37, i64 1604
  store volatile i32 %129, ptr %130, align 4, !tbaa !46
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.8) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %129) #7
  %131 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %131, align 1, !tbaa !23
  %132 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %126, i64 noundef 0, ptr noundef nonnull %3) #7
  %133 = icmp eq i64 %126, 0
  br i1 %133, label %134, label %139

134:                                              ; preds = %121
  %135 = getelementptr inbounds nuw i8, ptr %37, i64 1640
  %136 = getelementptr inbounds nuw i8, ptr %37, i64 1608
  %137 = getelementptr inbounds nuw i8, ptr %37, i64 1656
  %138 = getelementptr inbounds nuw i8, ptr %37, i64 1612
  br label %219

139:                                              ; preds = %121
  store volatile i32 2, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 %129, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  br label %260

140:                                              ; preds = %197, %152
  %141 = phi i64 [ %144, %152 ], [ %198, %197 ]
  %142 = icmp eq i64 %141, 7
  br i1 %142, label %236, label %143

143:                                              ; preds = %140
  %144 = add nuw nsw i64 %141, 1
  %145 = trunc nuw nsw i64 %144 to i32
  store volatile i32 %145, ptr %135, align 8, !tbaa !47
  %146 = icmp samesign ult i64 %141, 3
  br i1 %146, label %152, label %147

147:                                              ; preds = %143
  %148 = icmp samesign ult i64 %141, 5
  br i1 %148, label %152, label %149

149:                                              ; preds = %147
  %150 = icmp eq i64 %141, 5
  %151 = select i1 %150, i64 %122, i64 %70
  br label %152

152:                                              ; preds = %149, %147, %143
  %153 = phi i64 [ %69, %143 ], [ %151, %149 ], [ %123, %147 ]
  %154 = icmp eq i64 %153, 0
  br i1 %154, label %140, label %155, !llvm.loop !48

155:                                              ; preds = %152
  %156 = getelementptr inbounds nuw [24 x i8], ptr @candidates, i64 %141
  %157 = icmp eq i64 %199, 0
  br i1 %157, label %175, label %158

158:                                              ; preds = %155
  %159 = getelementptr inbounds nuw i8, ptr %156, i64 4
  %160 = load i32, ptr %159, align 4, !tbaa !49
  %161 = icmp eq i32 %222, %160
  br i1 %161, label %162, label %166

162:                                              ; preds = %158
  %163 = getelementptr inbounds nuw i8, ptr %156, i64 2
  %164 = load i8, ptr %163, align 2, !tbaa !51
  %165 = icmp eq i8 %223, %164
  br i1 %165, label %200, label %166

166:                                              ; preds = %162, %158
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.9) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %199) #7
  %167 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %167, align 1, !tbaa !23
  %168 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %199, i64 noundef 0, ptr noundef nonnull %3) #7
  %169 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef %59, i64 noundef %199, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %170 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %171 = add i32 %170, 1
  store volatile i32 %171, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.10) #7
  %172 = trunc i64 %169 to i32
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %172) #7
  %173 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %173, align 1, !tbaa !23
  %174 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %169, i64 noundef 0, ptr noundef nonnull %3) #7
  br label %175

175:                                              ; preds = %166, %155
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.11) #7
  %176 = getelementptr inbounds nuw i8, ptr %156, i64 4
  %177 = load i32, ptr %176, align 4, !tbaa !49
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %177) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.12) #7
  %178 = getelementptr inbounds nuw i8, ptr %156, i64 2
  %179 = load i8, ptr %178, align 2, !tbaa !51
  %180 = zext i8 %179 to i32
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %180) #7
  %181 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %181, align 1, !tbaa !23
  %182 = zext i32 %177 to i64
  %183 = zext i8 %179 to i64
  %184 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %182, i64 noundef %183, ptr noundef nonnull %3) #7
  %185 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef %59, i64 noundef %182, i64 noundef %183, i64 noundef 0, i64 noundef 0) #6
  %186 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %187 = add i32 %186, 1
  store volatile i32 %187, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %188 = trunc i64 %185 to i32
  store volatile i32 %188, ptr %136, align 8, !tbaa !52
  %189 = icmp eq i64 %185, 0
  br i1 %189, label %190, label %194

190:                                              ; preds = %175
  %191 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !53
  store volatile i64 %191, ptr %137, align 8, !tbaa !54
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.14) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %191) #7
  %192 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %192, align 1, !tbaa !23
  %193 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef 0, i64 noundef %191, ptr noundef nonnull %3) #7
  br label %200

194:                                              ; preds = %175
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.13) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %188) #7
  %195 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %195, align 1, !tbaa !23
  %196 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %185, i64 noundef 0, ptr noundef nonnull %3) #7
  br label %197, !llvm.loop !48

197:                                              ; preds = %219, %194
  %198 = phi i64 [ %144, %194 ], [ %220, %219 ]
  %199 = phi i64 [ 0, %194 ], [ %221, %219 ]
  br label %140

200:                                              ; preds = %162, %190
  %201 = phi i64 [ %191, %190 ], [ %199, %162 ]
  %202 = phi i32 [ %177, %190 ], [ %222, %162 ]
  %203 = phi i8 [ %179, %190 ], [ %223, %162 ]
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.15) #7
  %204 = load i8, ptr %156, align 8, !tbaa !55
  %205 = zext i8 %204 to i32
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %205) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.16) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %153) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.17) #7
  %206 = getelementptr inbounds nuw i8, ptr %156, i64 8
  %207 = load i32, ptr %206, align 8, !tbaa !56
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %207) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.18) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef -2305843009213691904) #7
  %208 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %208, align 1, !tbaa !23
  %209 = zext i32 %207 to i64
  %210 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %153, i64 noundef %209, ptr noundef nonnull %3) #7
  %211 = call i64 @lv1_hcall(i64 noundef 176, i64 noundef 4, i64 noundef %59, i64 noundef %153, i64 noundef %201, i64 noundef %209, i64 noundef -2305843009213691904) #6
  %212 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %213 = add i32 %212, 1
  store volatile i32 %213, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %214 = trunc i64 %211 to i32
  store volatile i32 %214, ptr %138, align 4, !tbaa !57
  %215 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !53
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.19) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %205) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.20) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %214) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.21) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %215) #7
  %216 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %216, align 1, !tbaa !23
  %217 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %211, i64 noundef %215, ptr noundef nonnull %3) #7
  %218 = icmp eq i64 %211, 0
  br i1 %218, label %224, label %219, !llvm.loop !48

219:                                              ; preds = %134, %200
  %220 = phi i64 [ 0, %134 ], [ %144, %200 ]
  %221 = phi i64 [ 0, %134 ], [ %201, %200 ]
  %222 = phi i32 [ 0, %134 ], [ %202, %200 ]
  %223 = phi i8 [ 0, %134 ], [ %203, %200 ]
  br label %197

224:                                              ; preds = %200
  %225 = getelementptr inbounds nuw i8, ptr %37, i64 1636
  store volatile i32 %205, ptr %225, align 4, !tbaa !58
  %226 = getelementptr inbounds nuw i8, ptr %37, i64 1664
  store volatile i64 %215, ptr %226, align 8, !tbaa !59
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.22) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %201) #7
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.17) #7
  call fastcc void @format_hex32(ptr noundef %4, i32 noundef zeroext %207) #7
  %227 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %227, align 1, !tbaa !23
  %228 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %201, i64 noundef %209, ptr noundef nonnull %3) #7
  %229 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef %59, i64 noundef %201, i64 noundef %209, i64 noundef 0, i64 noundef 0) #6
  %230 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %231 = add i32 %230, 1
  store volatile i32 %231, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %232 = trunc i64 %229 to i32
  %233 = getelementptr inbounds nuw i8, ptr %37, i64 1616
  store volatile i32 %232, ptr %233, align 8, !tbaa !60
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.23) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %232) #7
  %234 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %234, align 1, !tbaa !23
  %235 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %229, i64 noundef 0, ptr noundef nonnull %3) #7
  br label %236

236:                                              ; preds = %140, %224
  %237 = phi i32 [ %205, %224 ], [ 0, %140 ]
  %238 = phi i64 [ %201, %224 ], [ %199, %140 ]
  %239 = icmp eq i64 %238, 0
  br i1 %239, label %250, label %240

240:                                              ; preds = %236
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.9) #7
  call fastcc void @format_hex64(ptr noundef %4, i64 noundef %238) #7
  %241 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %241, align 1, !tbaa !23
  %242 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef %238, i64 noundef 0, ptr noundef nonnull %3) #7
  %243 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef %59, i64 noundef %238, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %244 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %245 = add i32 %244, 1
  store volatile i32 %245, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %246 = trunc i64 %243 to i32
  %247 = getelementptr inbounds nuw i8, ptr %37, i64 1620
  store volatile i32 %246, ptr %247, align 4, !tbaa !61
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.10) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %246) #7
  %248 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %248, align 1, !tbaa !23
  %249 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %243, i64 noundef 0, ptr noundef nonnull %3) #7
  br label %250

250:                                              ; preds = %240, %236
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.24) #7
  %251 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %251, align 1, !tbaa !23
  %252 = call signext i32 @hddlog_write(i32 noundef zeroext 1347568928, i64 noundef 4, i64 noundef %59, ptr noundef nonnull %3) #7
  %253 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef %59, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %254 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %255 = add i32 %254, 1
  store volatile i32 %255, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %256 = trunc i64 %253 to i32
  %257 = getelementptr inbounds nuw i8, ptr %37, i64 1624
  store volatile i32 %256, ptr %257, align 8, !tbaa !62
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.25) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %256) #7
  %258 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %258, align 1, !tbaa !23
  %259 = call signext i32 @hddlog_write(i32 noundef zeroext 1347375956, i64 noundef %253, i64 noundef 0, ptr noundef nonnull %3) #7
  br label %260

260:                                              ; preds = %250, %139
  %261 = phi i32 [ 0, %139 ], [ %237, %250 ]
  store ptr %3, ptr %4, align 8, !tbaa !32
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.26) #7
  %262 = icmp eq i32 %261, 0
  br i1 %262, label %264, label %263

263:                                              ; preds = %260
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull @.str.27) #7
  call fastcc void @format_dec(ptr noundef %4, i32 noundef zeroext %261) #7
  br label %264

264:                                              ; preds = %263, %260
  %265 = phi ptr [ @.str.28, %263 ], [ @.str.29, %260 ]
  %266 = phi i32 [ 0, %263 ], [ 4, %260 ]
  %267 = phi i32 [ 0, %263 ], [ -17, %260 ]
  call fastcc void @append_str(ptr noundef %4, ptr noundef nonnull %265) #7
  store volatile i32 %266, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  store volatile i32 %267, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !41
  %268 = load ptr, ptr %4, align 8, !tbaa !32
  store i8 0, ptr %268, align 1, !tbaa !23
  br label %269

269:                                              ; preds = %101, %264
  %270 = phi i32 [ %261, %264 ], [ %105, %101 ]
  %271 = zext i32 %270 to i64
  %272 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  %273 = zext i32 %272 to i64
  %274 = call signext i32 @hddlog_write(i32 noundef zeroext 1162757152, i64 noundef %271, i64 noundef %273, ptr noundef nonnull %3) #7
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #8
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #8
  %275 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  %276 = or i32 %275, 2
  store volatile i32 %276, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !28
  br label %277

277:                                              ; preds = %269, %47
  %278 = getelementptr inbounds nuw i8, ptr %37, i64 1024
  %279 = zext nneg i32 %10 to i64
  %280 = getelementptr inbounds nuw [64 x i8], ptr %278, i64 %279
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #8
  store ptr %280, ptr %2, align 8, !tbaa !32
  switch i32 %10, label %326 [
    i32 0, label %281
    i32 1, label %292
    i32 2, label %299
    i32 3, label %302
    i32 4, label %307
    i32 5, label %312
    i32 6, label %321
  ]

281:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.31) #7
  %282 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !40
  %283 = icmp eq i32 %282, 1
  br i1 %283, label %290, label %284

284:                                              ; preds = %281
  %285 = getelementptr inbounds nuw i8, ptr %37, i64 1636
  %286 = load volatile i32, ptr %285, align 4, !tbaa !58
  %287 = icmp eq i32 %286, 0
  br i1 %287, label %290, label %288

288:                                              ; preds = %284
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.33) #7
  %289 = load volatile i32, ptr %285, align 4, !tbaa !58
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %289) #7
  br label %290

290:                                              ; preds = %288, %284, %281
  %291 = phi ptr [ @.str.34, %288 ], [ @.str.32, %281 ], [ @.str.35, %284 ]
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull %291) #7
  br label %327

292:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.36) #7
  %293 = getelementptr inbounds nuw i8, ptr %37, i64 1636
  %294 = load volatile i32, ptr %293, align 4, !tbaa !58
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %294) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.37) #7
  %295 = getelementptr inbounds nuw i8, ptr %37, i64 1640
  %296 = load volatile i32, ptr %295, align 8, !tbaa !47
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %296) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.38) #7
  %297 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !45
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %297) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.39) #7
  %298 = load volatile i32, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !26
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %298) #7
  br label %327

299:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.40) #7
  %300 = getelementptr inbounds nuw i8, ptr %37, i64 1672
  %301 = load volatile i64, ptr %300, align 8, !tbaa !42
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %301) #7
  br label %327

302:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.41) #7
  %303 = getelementptr inbounds nuw i8, ptr %37, i64 1680
  %304 = load volatile i64, ptr %303, align 8, !tbaa !43
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %304) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.42) #7
  %305 = getelementptr inbounds nuw i8, ptr %37, i64 1688
  %306 = load volatile i64, ptr %305, align 8, !tbaa !44
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %306) #7
  br label %327

307:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.43) #7
  %308 = getelementptr inbounds nuw i8, ptr %37, i64 1656
  %309 = load volatile i64, ptr %308, align 8, !tbaa !54
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %309) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.44) #7
  %310 = getelementptr inbounds nuw i8, ptr %37, i64 1664
  %311 = load volatile i64, ptr %310, align 8, !tbaa !59
  call fastcc void @format_hex64(ptr noundef %2, i64 noundef %311) #7
  br label %327

312:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.45) #7
  %313 = getelementptr inbounds nuw i8, ptr %37, i64 1604
  %314 = load volatile i32, ptr %313, align 4, !tbaa !46
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %314) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.46) #7
  %315 = getelementptr inbounds nuw i8, ptr %37, i64 1608
  %316 = load volatile i32, ptr %315, align 8, !tbaa !52
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %316) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.47) #7
  %317 = getelementptr inbounds nuw i8, ptr %37, i64 1612
  %318 = load volatile i32, ptr %317, align 4, !tbaa !57
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %318) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.48) #7
  %319 = getelementptr inbounds nuw i8, ptr %37, i64 1624
  %320 = load volatile i32, ptr %319, align 8, !tbaa !62
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %320) #7
  br label %327

321:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.49) #7
  %322 = load volatile i32, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !36
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %322) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.50) #7
  %323 = load volatile i32, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !37
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %323) #7
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.51) #7
  %324 = getelementptr inbounds nuw i8, ptr %37, i64 1632
  %325 = load volatile i32, ptr %324, align 8, !tbaa !35
  call fastcc void @format_dec(ptr noundef %2, i32 noundef zeroext %325) #7
  br label %327

326:                                              ; preds = %277
  call fastcc void @append_str(ptr noundef %2, ptr noundef nonnull @.str.52) #7
  br label %327

327:                                              ; preds = %290, %292, %299, %302, %307, %312, %321, %326
  %328 = load ptr, ptr %2, align 8, !tbaa !32
  store i8 0, ptr %328, align 1, !tbaa !23
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #8
  br label %329

329:                                              ; preds = %33, %13, %327
  %330 = phi ptr [ %280, %327 ], [ inttoptr (i64 3165888 to ptr), %33 ], [ inttoptr (i64 3165888 to ptr), %13 ]
  ret ptr %330
}

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc ptr @get_arena() unnamed_addr #4 {
  %1 = load volatile i64, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !8
  %2 = tail call fastcc signext i32 @arena_rw(i64 noundef %1) #7
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
  br label %3, !llvm.loop !63

11:                                               ; preds = %3
  ret void
}

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_dec(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #5 {
  %3 = alloca [12 x i8], align 1
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #8
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
  br label %8, !llvm.loop !64

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
  br label %21, !llvm.loop !65

30:                                               ; preds = %21, %5
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #8
  ret void
}

; Function Attrs: minsize optsize
declare i64 @lv1_hcall(i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex64(ptr nofree noundef nonnull captures(none) %0, i64 noundef %1) unnamed_addr #5 {
  br label %3

3:                                                ; preds = %7, %2
  %4 = phi i32 [ 60, %2 ], [ %15, %7 ]
  %5 = icmp sgt i32 %4, -1
  br i1 %5, label %7, label %6

6:                                                ; preds = %3
  ret void

7:                                                ; preds = %3
  %8 = zext nneg i32 %4 to i64
  %9 = lshr i64 %1, %8
  %10 = and i64 %9, 15
  %11 = getelementptr inbounds nuw i8, ptr @__const.format_hex32.hex, i64 %10
  %12 = load i8, ptr %11, align 1, !tbaa !23
  %13 = load ptr, ptr %0, align 8, !tbaa !32
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 1
  store ptr %14, ptr %0, align 8, !tbaa !32
  store i8 %12, ptr %13, align 1, !tbaa !23
  %15 = add nsw i32 %4, -4
  br label %3, !llvm.loop !66
}

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none)
define internal fastcc void @format_hex32(ptr nofree noundef nonnull captures(none) %0, i32 noundef zeroext %1) unnamed_addr #5 {
  br label %3

3:                                                ; preds = %7, %2
  %4 = phi i32 [ 28, %2 ], [ %15, %7 ]
  %5 = icmp sgt i32 %4, -1
  br i1 %5, label %7, label %6

6:                                                ; preds = %3
  ret void

7:                                                ; preds = %3
  %8 = lshr i32 %1, %4
  %9 = and i32 %8, 15
  %10 = zext nneg i32 %9 to i64
  %11 = getelementptr inbounds nuw i8, ptr @__const.format_hex32.hex, i64 %10
  %12 = load i8, ptr %11, align 1, !tbaa !23
  %13 = load ptr, ptr %0, align 8, !tbaa !32
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 1
  store ptr %14, ptr %0, align 8, !tbaa !32
  store i8 %12, ptr %13, align 1, !tbaa !23
  %15 = add nsw i32 %4, -4
  br label %3, !llvm.loop !67
}

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #3 = { minsize nofree norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #4 = { minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #5 = { minsize nofree norecurse nosync nounwind optsize memory(write, argmem: readwrite, inaccessiblemem: none) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+altivec,+fpu,+fres,+frsqrte,+fsqrt,+hard-float,+mfocrf,+stfiwx" }
attributes #6 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #7 = { minsize nobuiltin optsize "no-builtins" }
attributes #8 = { nounwind }

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
!12 = !{!13, !5, i64 1644}
!13 = !{!"ProbeArena", !6, i64 0, !6, i64 512, !6, i64 1024, !5, i64 1600, !5, i64 1604, !5, i64 1608, !5, i64 1612, !5, i64 1616, !5, i64 1620, !5, i64 1624, !5, i64 1628, !5, i64 1632, !5, i64 1636, !5, i64 1640, !5, i64 1644, !5, i64 1648, !5, i64 1652, !10, i64 1656, !10, i64 1664, !10, i64 1672, !10, i64 1680, !10, i64 1688, !10, i64 1696}
!14 = !{!13, !10, i64 1696}
!15 = !{!13, !5, i64 1648}
!16 = !{!13, !5, i64 1652}
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
!35 = !{!13, !5, i64 1632}
!36 = !{!9, !5, i64 40}
!37 = !{!9, !5, i64 44}
!38 = !{!13, !5, i64 1628}
!39 = distinct !{!39, !22}
!40 = !{!9, !5, i64 12}
!41 = !{!9, !5, i64 16}
!42 = !{!13, !10, i64 1672}
!43 = !{!13, !10, i64 1680}
!44 = !{!13, !10, i64 1688}
!45 = !{!9, !5, i64 4}
!46 = !{!13, !5, i64 1604}
!47 = !{!13, !5, i64 1640}
!48 = distinct !{!48, !22}
!49 = !{!50, !5, i64 4}
!50 = !{!"MapCandidate", !6, i64 0, !6, i64 1, !6, i64 2, !5, i64 4, !5, i64 8, !10, i64 16}
!51 = !{!50, !6, i64 2}
!52 = !{!13, !5, i64 1608}
!53 = !{!9, !10, i64 80}
!54 = !{!13, !10, i64 1656}
!55 = !{!50, !6, i64 0}
!56 = !{!50, !5, i64 8}
!57 = !{!13, !5, i64 1612}
!58 = !{!13, !5, i64 1636}
!59 = !{!13, !10, i64 1664}
!60 = !{!13, !5, i64 1616}
!61 = !{!13, !5, i64 1620}
!62 = !{!13, !5, i64 1624}
!63 = distinct !{!63, !22}
!64 = distinct !{!64, !22}
!65 = distinct !{!65, !22}
!66 = distinct !{!66, !22}
!67 = distinct !{!67, !22}
