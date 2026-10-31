; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@labels_page_a = external constant [0 x i8], align 1
@labels_page_b = external constant [0 x i8], align 1
@labels_page_c = external constant [0 x i8], align 1
@labels_page_d = external constant [0 x i8], align 1
@str_sb_opt = internal constant [7 x i8] c"SB_OPT\00", align 1
@switch.table.s4_menu = private unnamed_addr constant [18 x i8] c"\0A\0B\0B\0B\0B\0B\09\08\07\0B\0B\06\05\04\03\02\0B\01", align 4

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  %5 = alloca i64, align 8
  %6 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %7 = and i32 %6, 1
  %8 = icmp eq i32 %7, 0
  br i1 %8, label %9, label %277

9:                                                ; preds = %1
  %10 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %11 = or i32 %10, 1
  store volatile i32 %11, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #5
  store i64 0, ptr %2, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #5
  store i64 0, ptr %3, align 8, !tbaa !9
  store volatile i8 -1, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !10
  store volatile i8 -1, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  store volatile i8 -1, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  store volatile i8 -1, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  store volatile i8 -1, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  store volatile i8 -1, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  store volatile i8 -1, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  store volatile i32 0, ptr inttoptr (i64 9637788 to ptr), align 4, !tbaa !17
  br label %12

12:                                               ; preds = %112, %9
  %13 = phi i64 [ %113, %112 ], [ 0, %9 ]
  %14 = icmp eq i64 %13, 16
  br i1 %14, label %15, label %21

15:                                               ; preds = %12
  %16 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %17 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %18 = add i32 %17, 1
  store volatile i32 %18, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %19 = trunc i64 %16 to i32
  store volatile i32 %19, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !19
  %20 = icmp eq i64 %16, 0
  br i1 %20, label %115, label %114

21:                                               ; preds = %12
  %22 = or disjoint i64 %13, 7094703231829278720
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %23 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #6
  %24 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %25 = add i32 %24, 1
  store volatile i32 %25, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %26 = icmp eq i64 %23, 0
  br i1 %26, label %32, label %27

27:                                               ; preds = %21
  %28 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %29 = icmp eq i32 %28, 0
  br i1 %29, label %30, label %112

30:                                               ; preds = %27
  %31 = trunc i64 %23 to i32
  store volatile i32 %31, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %112

32:                                               ; preds = %21
  %33 = load i64, ptr %2, align 8, !tbaa !9
  %34 = icmp eq i64 %33, 5
  %35 = trunc i64 %13 to i8
  br i1 %34, label %36, label %37

36:                                               ; preds = %32
  store volatile i8 %35, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !10
  br label %37

37:                                               ; preds = %36, %32
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %38 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #6
  %39 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %40 = add i32 %39, 1
  store volatile i32 %40, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %41 = icmp eq i64 %38, 0
  %42 = load i64, ptr %2, align 8
  %43 = select i1 %41, i64 %42, i64 0
  %44 = icmp eq i64 %13, 4
  br label %45

45:                                               ; preds = %110, %37
  %46 = phi i64 [ %111, %110 ], [ 0, %37 ]
  %47 = icmp eq i64 %46, 16
  br i1 %47, label %112, label %48

48:                                               ; preds = %45
  %49 = or disjoint i64 %46, 7234318118812647424
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %50 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8392862959675637760, i64 noundef 0) #6
  %51 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %52 = add i32 %51, 1
  store volatile i32 %52, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %53 = icmp eq i64 %46, 2
  %54 = and i1 %44, %53
  br i1 %54, label %55, label %57

55:                                               ; preds = %48
  %56 = trunc i64 %50 to i32
  store volatile i32 %56, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !21
  br label %57

57:                                               ; preds = %55, %48
  %58 = icmp eq i64 %50, 0
  br i1 %58, label %59, label %110

59:                                               ; preds = %57
  %60 = load i64, ptr %2, align 8, !tbaa !9
  %61 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %62 = add i32 %61, 1
  store volatile i32 %62, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %63 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 7594194871653498880, i64 noundef 0) #6
  %64 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %65 = add i32 %64, 1
  store volatile i32 %65, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %66 = icmp eq i64 %63, 0
  %67 = load i64, ptr %2, align 8
  %68 = select i1 %66, i64 %67, i64 0
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %69 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8101820097204584448, i64 noundef 0) #6
  %70 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %71 = add i32 %70, 1
  store volatile i32 %71, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %72 = icmp eq i64 %69, 0
  %73 = load i64, ptr %2, align 8
  %74 = trunc i64 %73 to i32
  %75 = select i1 %72, i32 %74, i32 255
  %76 = icmp eq i64 %60, 5
  br i1 %76, label %77, label %100

77:                                               ; preds = %59
  %78 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %79 = add i32 %78, 1
  store volatile i32 %79, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %80 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %81 = icmp eq i32 %80, 1
  br i1 %81, label %82, label %92

82:                                               ; preds = %77
  store volatile i8 %35, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %83 = trunc i64 %46 to i8
  store volatile i8 %83, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %84 = trunc i32 %75 to i8
  store volatile i8 %84, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  store volatile i64 %43, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !24
  store volatile i64 %68, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !25
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %85 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8243108395510267904, i64 noundef 7594194871653498880) #6
  %86 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %87 = add i32 %86, 1
  store volatile i32 %87, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %88 = icmp eq i64 %85, 0
  br i1 %88, label %89, label %92

89:                                               ; preds = %82
  %90 = load i64, ptr %2, align 8, !tbaa !9
  %91 = trunc i64 %90 to i32
  store volatile i32 %91, ptr inttoptr (i64 9637788 to ptr), align 4, !tbaa !17
  br label %92

92:                                               ; preds = %89, %82, %77
  br i1 %34, label %93, label %96

93:                                               ; preds = %92
  %94 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %95 = or i8 %94, 1
  store volatile i8 %95, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  br label %96

96:                                               ; preds = %93, %92
  br i1 %44, label %97, label %110

97:                                               ; preds = %96
  %98 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %99 = or i8 %98, 2
  store volatile i8 %99, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  br label %110

100:                                              ; preds = %59
  %101 = icmp eq i64 %60, 0
  %102 = select i1 %44, i1 %101, i1 false
  %103 = icmp eq i32 %75, 2
  %104 = select i1 %102, i1 %103, i1 false
  br i1 %104, label %105, label %110

105:                                              ; preds = %100
  %106 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %107 = icmp eq i32 %106, 0
  br i1 %107, label %108, label %110

108:                                              ; preds = %105
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  store volatile i8 4, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %109 = trunc i64 %46 to i8
  store volatile i8 %109, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  store volatile i8 2, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  br label %110

110:                                              ; preds = %108, %105, %100, %97, %96, %57
  %111 = add nuw nsw i64 %46, 1
  br label %45, !llvm.loop !28

112:                                              ; preds = %45, %30, %27
  %113 = add nuw nsw i64 %13, 1
  br label %12, !llvm.loop !30

114:                                              ; preds = %15
  store volatile i32 1, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %19, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %274

115:                                              ; preds = %15
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #5
  store i64 0, ptr %4, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #5
  store i64 0, ptr %5, align 8, !tbaa !9
  %116 = call i64 @alloc_buffer(ptr noundef nonnull @str_sb_opt, i64 noundef 1048576, ptr noundef nonnull %4, ptr noundef nonnull %5) #6
  %117 = trunc i64 %116 to i32
  store volatile i32 %117, ptr inttoptr (i64 9637780 to ptr), align 4, !tbaa !32
  %118 = load i64, ptr %4, align 8, !tbaa !9
  store volatile i64 %118, ptr inttoptr (i64 9637800 to ptr), align 8, !tbaa !33
  %119 = load i64, ptr %5, align 8, !tbaa !9
  store volatile i64 %119, ptr inttoptr (i64 9637792 to ptr), align 32, !tbaa !34
  %120 = icmp ne i64 %116, 0
  %121 = icmp eq i64 %119, 0
  %122 = select i1 %120, i1 true, i1 %121
  %123 = load i64, ptr %4, align 8
  %124 = icmp eq i64 %123, 0
  %125 = select i1 %122, i1 true, i1 %124
  br i1 %125, label %126, label %131

126:                                              ; preds = %115
  store volatile i32 2, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %117, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %127 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %128 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %129 = add i32 %128, 1
  store volatile i32 %129, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %130 = trunc i64 %127 to i32
  store volatile i32 %130, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %273

131:                                              ; preds = %115
  %132 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef 2, i64 noundef 524288, i64 noundef 12, i64 noundef 0, i64 noundef 0) #6
  %133 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %134 = add i32 %133, 1
  store volatile i32 %134, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %135 = trunc i64 %132 to i32
  store volatile i32 %135, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !36
  %136 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  store volatile i64 %136, ptr inttoptr (i64 9637808 to ptr), align 16, !tbaa !38
  %137 = icmp eq i64 %132, 0
  br i1 %137, label %143, label %138

138:                                              ; preds = %131
  store volatile i32 3, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %135, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %139 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %140 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %141 = add i32 %140, 1
  store volatile i32 %141, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %142 = trunc i64 %139 to i32
  store volatile i32 %142, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %273

143:                                              ; preds = %131
  %144 = load i64, ptr %5, align 8, !tbaa !9
  %145 = call i64 @lv1_hcall(i64 noundef 176, i64 noundef 4, i64 noundef 2, i64 noundef %144, i64 noundef %136, i64 noundef 524288, i64 noundef -2305843009213691904) #6
  %146 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %147 = add i32 %146, 1
  store volatile i32 %147, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %148 = trunc i64 %145 to i32
  store volatile i32 %148, ptr inttoptr (i64 9637716 to ptr), align 4, !tbaa !39
  %149 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  store volatile i64 %149, ptr inttoptr (i64 9637816 to ptr), align 8, !tbaa !40
  %150 = icmp eq i64 %145, 0
  br i1 %150, label %160, label %151

151:                                              ; preds = %143
  store volatile i32 4, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %148, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %152 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %153 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %154 = add i32 %153, 1
  store volatile i32 %154, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %155 = trunc i64 %152 to i32
  store volatile i32 %155, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !41
  %156 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %157 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %158 = add i32 %157, 1
  store volatile i32 %158, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %159 = trunc i64 %156 to i32
  store volatile i32 %159, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %273

160:                                              ; preds = %143
  %161 = load i64, ptr %4, align 8, !tbaa !9
  %162 = inttoptr i64 %161 to ptr
  %163 = load i64, ptr %5, align 8, !tbaa !9
  %164 = add i64 %163, 4096
  call fastcc void @setup_atapi_block(ptr noundef %162, i8 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i32 noundef zeroext 0, i64 noundef 0, i32 noundef zeroext 0) #7
  %165 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef 2, i64 noundef 1, i64 noundef %163, i64 noundef 64, i64 noundef 0, i64 noundef 0) #6
  %166 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %167 = add i32 %166, 1
  store volatile i32 %167, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %168 = trunc i64 %165 to i32
  store volatile i32 %168, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !42
  %169 = icmp eq i64 %165, 0
  br i1 %169, label %170, label %177

170:                                              ; preds = %160
  %171 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  %172 = call fastcc signext i32 @poll_completion(i64 noundef %171, ptr noundef nonnull inttoptr (i64 9637824 to ptr)) #7
  %173 = icmp eq i32 %172, 0
  br i1 %173, label %178, label %174

174:                                              ; preds = %170
  %175 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %176 = or i32 %175, 1
  store volatile i32 %176, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  store volatile i32 5, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %273

177:                                              ; preds = %160
  store volatile i32 5, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %168, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %178

178:                                              ; preds = %177, %170
  call fastcc void @setup_atapi_block(ptr noundef %162, i8 noundef zeroext 18, i32 noundef zeroext 36, i32 noundef zeroext 1, i32 noundef zeroext 1, i64 noundef %164, i32 noundef zeroext 36) #7
  %179 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef 2, i64 noundef 1, i64 noundef %163, i64 noundef 64, i64 noundef %164, i64 noundef 36) #6
  %180 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %181 = add i32 %180, 1
  store volatile i32 %181, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %182 = trunc i64 %179 to i32
  store volatile i32 %182, ptr inttoptr (i64 9637724 to ptr), align 4, !tbaa !44
  %183 = icmp eq i64 %179, 0
  br i1 %183, label %184, label %191

184:                                              ; preds = %178
  %185 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  %186 = call fastcc signext i32 @poll_completion(i64 noundef %185, ptr noundef nonnull inttoptr (i64 9637832 to ptr)) #7
  %187 = icmp eq i32 %186, 0
  br i1 %187, label %199, label %188

188:                                              ; preds = %184
  %189 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %190 = or i32 %189, 2
  store volatile i32 %190, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  store volatile i32 6, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %273

191:                                              ; preds = %178
  %192 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %193 = icmp eq i32 %192, 0
  br i1 %193, label %194, label %195

194:                                              ; preds = %191
  store volatile i32 6, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %195

195:                                              ; preds = %194, %191
  %196 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %197 = icmp eq i32 %196, 0
  br i1 %197, label %198, label %199

198:                                              ; preds = %195
  store volatile i32 %182, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %199

199:                                              ; preds = %198, %195, %184
  call fastcc void @setup_atapi_block(ptr noundef %162, i8 noundef zeroext 37, i32 noundef zeroext 8, i32 noundef zeroext 1, i32 noundef zeroext 1, i64 noundef %164, i32 noundef zeroext 8) #7
  %200 = call i64 @lv1_hcall(i64 noundef 248, i64 noundef 2, i64 noundef 1, i64 noundef %163, i64 noundef 64, i64 noundef %164, i64 noundef 8) #6
  %201 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %202 = add i32 %201, 1
  store volatile i32 %202, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %203 = trunc i64 %200 to i32
  store volatile i32 %203, ptr inttoptr (i64 9637760 to ptr), align 128, !tbaa !45
  %204 = icmp eq i64 %200, 0
  br i1 %204, label %205, label %212

205:                                              ; preds = %199
  %206 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  %207 = call fastcc signext i32 @poll_completion(i64 noundef %206, ptr noundef nonnull inttoptr (i64 9637840 to ptr)) #7
  %208 = icmp eq i32 %207, 0
  br i1 %208, label %220, label %209

209:                                              ; preds = %205
  %210 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %211 = or i32 %210, 4
  store volatile i32 %211, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  store volatile i32 7, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %273

212:                                              ; preds = %199
  %213 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %214 = icmp eq i32 %213, 0
  br i1 %214, label %215, label %216

215:                                              ; preds = %212
  store volatile i32 7, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %216

216:                                              ; preds = %215, %212
  %217 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %218 = icmp eq i32 %217, 0
  br i1 %218, label %219, label %220

219:                                              ; preds = %216
  store volatile i32 %203, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %220

220:                                              ; preds = %219, %216, %205
  %221 = load volatile i32, ptr inttoptr (i64 9637788 to ptr), align 4, !tbaa !17
  %222 = zext i32 %221 to i64
  %223 = call i64 @lv1_hcall(i64 noundef 245, i64 noundef 2, i64 noundef %222, i64 noundef 16, i64 noundef 1, i64 noundef 0, i64 noundef %164) #6
  %224 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %225 = add i32 %224, 1
  store volatile i32 %225, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %226 = trunc i64 %223 to i32
  store volatile i32 %226, ptr inttoptr (i64 9637764 to ptr), align 4, !tbaa !46
  %227 = icmp eq i64 %223, 0
  br i1 %227, label %228, label %235

228:                                              ; preds = %220
  %229 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  %230 = call fastcc signext i32 @poll_completion(i64 noundef %229, ptr noundef nonnull inttoptr (i64 9637848 to ptr)) #7
  %231 = icmp eq i32 %230, 0
  br i1 %231, label %243, label %232

232:                                              ; preds = %228
  %233 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %234 = or i32 %233, 8
  store volatile i32 %234, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  store volatile i32 8, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %273

235:                                              ; preds = %220
  %236 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %237 = icmp eq i32 %236, 0
  br i1 %237, label %238, label %239

238:                                              ; preds = %235
  store volatile i32 8, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  br label %239

239:                                              ; preds = %238, %235
  %240 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %241 = icmp eq i32 %240, 0
  br i1 %241, label %242, label %243

242:                                              ; preds = %239
  store volatile i32 %226, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %243

243:                                              ; preds = %242, %239, %228
  %244 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 524288, i64 noundef 0, i64 noundef 0) #6
  %245 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %246 = add i32 %245, 1
  store volatile i32 %246, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %247 = trunc i64 %244 to i32
  store volatile i32 %247, ptr inttoptr (i64 9637768 to ptr), align 8, !tbaa !47
  %248 = icmp eq i64 %244, 0
  br i1 %248, label %253, label %249

249:                                              ; preds = %243
  %250 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %251 = icmp eq i32 %250, 0
  br i1 %251, label %252, label %253

252:                                              ; preds = %249
  store volatile i32 9, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %247, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %253

253:                                              ; preds = %252, %249, %243
  %254 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %255 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %256 = add i32 %255, 1
  store volatile i32 %256, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %257 = trunc i64 %254 to i32
  store volatile i32 %257, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !41
  %258 = icmp eq i64 %254, 0
  br i1 %258, label %263, label %259

259:                                              ; preds = %253
  %260 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %261 = icmp eq i32 %260, 0
  br i1 %261, label %262, label %263

262:                                              ; preds = %259
  store volatile i32 10, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %257, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %263

263:                                              ; preds = %262, %259, %253
  %264 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %265 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %266 = add i32 %265, 1
  store volatile i32 %266, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %267 = trunc i64 %264 to i32
  store volatile i32 %267, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  %268 = icmp eq i64 %264, 0
  br i1 %268, label %273, label %269

269:                                              ; preds = %263
  %270 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %271 = icmp eq i32 %270, 0
  br i1 %271, label %272, label %273

272:                                              ; preds = %269
  store volatile i32 11, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %267, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %273

273:                                              ; preds = %272, %269, %263, %232, %209, %188, %174, %151, %138, %126
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #5
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #5
  br label %274

274:                                              ; preds = %114, %273
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #5
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #5
  %275 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %276 = or i32 %275, 2
  store volatile i32 %276, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %277

277:                                              ; preds = %274, %1
  %278 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %279 = and i32 %278, 2
  %280 = icmp eq i32 %279, 0
  br i1 %280, label %469, label %281

281:                                              ; preds = %277
  %282 = trunc i64 %0 to i32
  %283 = and i32 %282, 3
  switch i32 %283, label %468 [
    i32 0, label %284
    i32 1, label %325
    i32 2, label %349
    i32 3, label %401
  ]

284:                                              ; preds = %281
  %285 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %286 = icmp eq i32 %285, 0
  br i1 %286, label %303, label %287

287:                                              ; preds = %284
  %288 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %289 = and i32 %288, 1
  %290 = icmp eq i32 %289, 0
  br i1 %290, label %291, label %469

291:                                              ; preds = %287
  %292 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %293 = and i32 %292, 2
  %294 = icmp eq i32 %293, 0
  br i1 %294, label %295, label %469

295:                                              ; preds = %291
  %296 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %297 = and i32 %296, 4
  %298 = icmp eq i32 %297, 0
  br i1 %298, label %299, label %469

299:                                              ; preds = %295
  %300 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %301 = and i32 %300, 8
  %302 = icmp eq i32 %301, 0
  br i1 %302, label %303, label %469

303:                                              ; preds = %299, %284
  %304 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %305 = icmp eq i32 %304, 0
  br i1 %305, label %469, label %306

306:                                              ; preds = %303
  %307 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %308 = call i32 @llvm.umin.i32(i32 %307, i32 11)
  %309 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %310 = add i32 %309, 17
  %311 = icmp ult i32 %310, 18
  br i1 %311, label %312, label %317

312:                                              ; preds = %306
  %313 = zext nneg i32 %310 to i64
  %314 = getelementptr inbounds nuw i8, ptr @switch.table.s4_menu, i64 %313
  %315 = load i8, ptr %314, align 1
  %316 = zext i8 %315 to i32
  br label %317

317:                                              ; preds = %306, %312
  %318 = phi i32 [ %316, %312 ], [ 11, %306 ]
  %319 = mul nuw nsw i32 %308, 12
  %320 = add nuw nsw i32 %319, 67108857
  %321 = add nuw nsw i32 %320, %318
  %322 = shl i32 %321, 6
  %323 = zext i32 %322 to i64
  %324 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %323
  br label %469

325:                                              ; preds = %281
  %326 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %327 = icmp eq i32 %326, 0
  br i1 %327, label %328, label %331

328:                                              ; preds = %325
  %329 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %330 = icmp eq i32 %329, 0
  br i1 %330, label %469, label %331

331:                                              ; preds = %328, %325
  %332 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %333 = icmp ugt i32 %332, -257
  br i1 %333, label %334, label %336

334:                                              ; preds = %331
  %335 = and i32 %332, 255
  br label %343

336:                                              ; preds = %331
  %337 = icmp ult i32 %332, 256
  br i1 %337, label %338, label %340

338:                                              ; preds = %336
  %339 = or disjoint i32 %332, 256
  br label %343

340:                                              ; preds = %336
  %341 = lshr i32 %332, 28
  %342 = or disjoint i32 %341, 512
  br label %343

343:                                              ; preds = %334, %338, %340
  %344 = phi i32 [ %335, %334 ], [ %339, %338 ], [ %342, %340 ]
  %345 = shl nuw nsw i32 %344, 6
  %346 = zext nneg i32 %345 to i64
  %347 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %346
  %348 = getelementptr inbounds nuw i8, ptr %347, i64 64
  br label %469

349:                                              ; preds = %281
  %350 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %351 = and i32 %350, 8
  %352 = icmp eq i32 %351, 0
  br i1 %352, label %353, label %469

353:                                              ; preds = %349
  %354 = load volatile i32, ptr inttoptr (i64 9637764 to ptr), align 4, !tbaa !46
  %355 = icmp eq i32 %354, 0
  br i1 %355, label %356, label %469

356:                                              ; preds = %353
  %357 = load volatile i64, ptr inttoptr (i64 9637848 to ptr), align 8, !tbaa !48
  %358 = icmp eq i64 %357, 0
  br i1 %358, label %366, label %359

359:                                              ; preds = %356
  %360 = load volatile i64, ptr inttoptr (i64 9637848 to ptr), align 8, !tbaa !48
  %361 = trunc i64 %360 to i32
  switch i32 %361, label %362 [
    i32 33700352, label %469
    i32 33890560, label %365
  ]

362:                                              ; preds = %359
  %363 = and i32 %361, 65535
  %364 = icmp eq i32 %363, 47
  br i1 %364, label %365, label %469

365:                                              ; preds = %359, %362
  br label %469

366:                                              ; preds = %356
  %367 = load volatile i64, ptr inttoptr (i64 9637800 to ptr), align 8, !tbaa !33
  %368 = add i64 %367, 4096
  %369 = inttoptr i64 %368 to ptr
  %370 = load volatile i8, ptr %369, align 1, !tbaa !49
  %371 = icmp eq i8 %370, 1
  br i1 %371, label %372, label %400

372:                                              ; preds = %366
  %373 = getelementptr inbounds nuw i8, ptr %369, i64 1
  %374 = load volatile i8, ptr %373, align 1, !tbaa !49
  %375 = icmp eq i8 %374, 67
  br i1 %375, label %376, label %400

376:                                              ; preds = %372
  %377 = getelementptr inbounds nuw i8, ptr %369, i64 2
  %378 = load volatile i8, ptr %377, align 1, !tbaa !49
  %379 = icmp eq i8 %378, 68
  br i1 %379, label %380, label %400

380:                                              ; preds = %376
  %381 = getelementptr inbounds nuw i8, ptr %369, i64 3
  %382 = load volatile i8, ptr %381, align 1, !tbaa !49
  %383 = icmp eq i8 %382, 48
  br i1 %383, label %384, label %400

384:                                              ; preds = %380
  %385 = getelementptr inbounds nuw i8, ptr %369, i64 4
  %386 = load volatile i8, ptr %385, align 1, !tbaa !49
  %387 = icmp eq i8 %386, 48
  br i1 %387, label %388, label %400

388:                                              ; preds = %384
  %389 = getelementptr inbounds nuw i8, ptr %369, i64 5
  %390 = load volatile i8, ptr %389, align 1, !tbaa !49
  %391 = icmp eq i8 %390, 49
  br i1 %391, label %392, label %400

392:                                              ; preds = %388
  %393 = getelementptr inbounds nuw i8, ptr %369, i64 6
  %394 = load volatile i8, ptr %393, align 1, !tbaa !49
  %395 = icmp eq i8 %394, 1
  br i1 %395, label %396, label %400

396:                                              ; preds = %392
  %397 = getelementptr inbounds nuw i8, ptr %369, i64 7
  %398 = load volatile i8, ptr %397, align 1, !tbaa !49
  %399 = icmp eq i8 %398, 0
  br i1 %399, label %469, label %400

400:                                              ; preds = %396, %392, %388, %384, %380, %376, %372, %366
  br label %469

401:                                              ; preds = %281
  %402 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %403 = icmp eq i32 %402, 0
  br i1 %403, label %426, label %404

404:                                              ; preds = %401
  %405 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %406 = icmp eq i8 %405, 4
  br i1 %406, label %407, label %413

407:                                              ; preds = %404
  %408 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %409 = icmp eq i8 %408, 2
  br i1 %409, label %410, label %413

410:                                              ; preds = %407
  %411 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  %412 = icmp eq i8 %411, 0
  br i1 %412, label %426, label %413

413:                                              ; preds = %410, %407, %404
  %414 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %415 = icmp eq i8 %414, 5
  br i1 %415, label %416, label %419

416:                                              ; preds = %413
  %417 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %418 = icmp eq i8 %417, 0
  br i1 %418, label %426, label %419

419:                                              ; preds = %416, %413
  %420 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %421 = icmp eq i8 %420, 4
  br i1 %421, label %422, label %425

422:                                              ; preds = %419
  %423 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %424 = icmp eq i8 %423, 2
  br i1 %424, label %426, label %425

425:                                              ; preds = %422, %419
  br label %426

426:                                              ; preds = %425, %422, %416, %410, %401
  %427 = phi i64 [ 0, %401 ], [ 901, %410 ], [ 1802, %416 ], [ 3604, %425 ], [ 2703, %422 ]
  %428 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %429 = icmp eq i32 %428, 0
  br i1 %429, label %462, label %430

430:                                              ; preds = %426
  %431 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %432 = icmp ult i8 %431, 8
  br i1 %432, label %433, label %437

433:                                              ; preds = %430
  %434 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %435 = zext i8 %434 to i64
  %436 = mul nuw nsw i64 %435, 5
  br label %437

437:                                              ; preds = %433, %430
  %438 = phi i64 [ %436, %433 ], [ 40, %430 ]
  %439 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %440 = icmp ult i8 %439, 4
  br i1 %440, label %441, label %444

441:                                              ; preds = %437
  %442 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %443 = zext i8 %442 to i64
  br label %444

444:                                              ; preds = %441, %437
  %445 = phi i64 [ %443, %441 ], [ 4, %437 ]
  %446 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %447 = icmp ult i8 %446, 4
  br i1 %447, label %448, label %451

448:                                              ; preds = %444
  %449 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %450 = zext i8 %449 to i64
  br label %451

451:                                              ; preds = %448, %444
  %452 = phi i64 [ %450, %448 ], [ 4, %444 ]
  %453 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %454 = and i8 %453, 3
  %455 = zext nneg i8 %454 to i64
  %456 = add nuw nsw i64 %445, %438
  %457 = mul nuw nsw i64 %456, 5
  %458 = add nuw nsw i64 %452, %457
  %459 = shl nuw nsw i64 %458, 2
  %460 = or disjoint i64 %459, 1
  %461 = add nuw nsw i64 %460, %455
  br label %462

462:                                              ; preds = %426, %451
  %463 = phi i64 [ %461, %451 ], [ 0, %426 ]
  %464 = add nuw nsw i64 %463, %427
  %465 = shl nuw nsw i64 %464, 6
  %466 = and i64 %465, 4294967232
  %467 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %466
  br label %469

468:                                              ; preds = %281
  unreachable

469:                                              ; preds = %317, %343, %462, %287, %291, %295, %299, %303, %328, %349, %353, %362, %359, %365, %396, %400, %277
  %470 = phi ptr [ inttoptr (i64 3165888 to ptr), %277 ], [ %467, %462 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 256), %362 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 64), %287 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 128), %291 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 192), %295 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 256), %299 ], [ %324, %317 ], [ @labels_page_a, %303 ], [ %348, %343 ], [ @labels_page_b, %328 ], [ @labels_page_c, %349 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 64), %353 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 128), %359 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 192), %365 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 384), %400 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 320), %396 ]
  ret ptr %470
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare i64 @lv1_hcall(i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare i64 @alloc_buffer(ptr noundef, i64 noundef, ptr noundef, ptr noundef) local_unnamed_addr #2

; Function Attrs: minsize nofree norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite)
define internal fastcc void @setup_atapi_block(ptr nofree noundef captures(address) %0, i8 noundef zeroext range(i8 0, 38) %1, i32 noundef zeroext range(i32 0, 37) %2, i32 noundef zeroext range(i32 0, 2) %3, i32 noundef zeroext range(i32 0, 2) %4, i64 noundef %5, i32 noundef zeroext range(i32 0, 37) %6) unnamed_addr #3 {
  br label %8

8:                                                ; preds = %13, %7
  %9 = phi i64 [ %15, %13 ], [ 0, %7 ]
  %10 = icmp eq i64 %9, 8
  br i1 %10, label %11, label %13

11:                                               ; preds = %8
  store volatile i8 %1, ptr %0, align 1, !tbaa !49
  %12 = icmp eq i8 %1, 18
  br i1 %12, label %16, label %19

13:                                               ; preds = %8
  %14 = getelementptr inbounds nuw [8 x i8], ptr %0, i64 %9
  store volatile i64 0, ptr %14, align 8, !tbaa !9
  %15 = add nuw nsw i64 %9, 1
  br label %8, !llvm.loop !50

16:                                               ; preds = %11
  %17 = trunc nuw nsw i32 %2 to i8
  %18 = getelementptr inbounds nuw i8, ptr %0, i64 4
  store volatile i8 %17, ptr %18, align 1, !tbaa !49
  br label %19

19:                                               ; preds = %16, %11
  %20 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store volatile i32 12, ptr %20, align 4, !tbaa !51
  %21 = getelementptr inbounds nuw i8, ptr %0, i64 36
  store volatile i32 %2, ptr %21, align 4, !tbaa !51
  %22 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store volatile i32 1, ptr %22, align 4, !tbaa !51
  %23 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store volatile i32 %3, ptr %23, align 4, !tbaa !51
  %24 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store volatile i32 %4, ptr %24, align 4, !tbaa !51
  %25 = getelementptr inbounds nuw i8, ptr %0, i64 56
  store volatile i64 %5, ptr %25, align 8, !tbaa !9
  %26 = getelementptr inbounds nuw i8, ptr %0, i64 64
  store volatile i32 %6, ptr %26, align 8, !tbaa !51
  ret void
}

; Function Attrs: minsize nounwind optsize
define internal fastcc signext range(i32 0, 2) i32 @poll_completion(i64 noundef %0, ptr nofree noundef captures(address) %1) unnamed_addr #0 {
  %3 = tail call i64 @native_clock() #6
  br label %4

4:                                                ; preds = %12, %2
  %5 = phi i32 [ 0, %2 ], [ %17, %12 ]
  %6 = icmp eq i32 %5, 200000
  br i1 %6, label %20, label %7

7:                                                ; preds = %4
  %8 = tail call i64 @lv1_hcall(i64 noundef 254, i64 noundef 2, i64 noundef %0, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %9 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %10 = add i32 %9, 1
  store volatile i32 %10, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %11 = icmp eq i64 %8, 0
  br i1 %11, label %18, label %12

12:                                               ; preds = %7
  %13 = tail call i64 @native_clock() #6
  %14 = sub i64 %13, %3
  %15 = trunc i64 %14 to i32
  %16 = icmp ugt i32 %15, 159999999
  %17 = add nuw nsw i32 %5, 1
  br i1 %16, label %20, label %4, !llvm.loop !52

18:                                               ; preds = %7
  %19 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !37
  store volatile i64 %19, ptr %1, align 8, !tbaa !9
  br label %20

20:                                               ; preds = %12, %4, %18
  %21 = phi i32 [ 0, %18 ], [ 1, %4 ], [ 1, %12 ]
  ret i32 %21
}

; Function Attrs: minsize optsize
declare i64 @native_clock() local_unnamed_addr #2

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #4

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #3 = { minsize nofree norecurse nosync nounwind optsize memory(argmem: readwrite, inaccessiblemem: readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #4 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nounwind }
attributes #6 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #7 = { minsize nobuiltin optsize "no-builtins" }

!llvm.ident = !{!0}
!llvm.errno.tbaa = !{!1}

!0 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!1 = !{!2, !3, i64 0}
!2 = !{!"__libc_errno", !3, i64 0}
!3 = !{!"int", !4, i64 0}
!4 = !{!"omnipotent char", !5, i64 0}
!5 = !{!"Simple C/C++ TBAA"}
!6 = !{!7, !3, i64 0}
!7 = !{!"ProbeState", !3, i64 0, !3, i64 4, !3, i64 8, !3, i64 12, !3, i64 16, !3, i64 20, !3, i64 24, !3, i64 28, !4, i64 32, !4, i64 33, !4, i64 34, !4, i64 35, !4, i64 36, !4, i64 37, !4, i64 38, !4, i64 39, !3, i64 40, !3, i64 44, !3, i64 48, !3, i64 52, !3, i64 56, !3, i64 60, !8, i64 64, !8, i64 72, !8, i64 80, !8, i64 88, !3, i64 96, !3, i64 100, !3, i64 104, !3, i64 108, !3, i64 112, !3, i64 116, !3, i64 120, !3, i64 124, !8, i64 128, !8, i64 136, !8, i64 144, !8, i64 152, !8, i64 160, !8, i64 168, !8, i64 176, !8, i64 184}
!8 = !{!"long long", !4, i64 0}
!9 = !{!8, !8, i64 0}
!10 = !{!7, !4, i64 35}
!11 = !{!7, !4, i64 32}
!12 = !{!7, !4, i64 33}
!13 = !{!7, !4, i64 34}
!14 = !{!7, !4, i64 36}
!15 = !{!7, !4, i64 37}
!16 = !{!7, !4, i64 38}
!17 = !{!7, !3, i64 124}
!18 = !{!7, !3, i64 20}
!19 = !{!7, !3, i64 44}
!20 = !{!7, !3, i64 24}
!21 = !{!7, !3, i64 40}
!22 = !{!7, !3, i64 4}
!23 = !{!7, !3, i64 8}
!24 = !{!7, !8, i64 64}
!25 = !{!7, !8, i64 72}
!26 = !{!7, !4, i64 39}
!27 = !{!7, !3, i64 12}
!28 = distinct !{!28, !29}
!29 = !{!"llvm.loop.mustprogress"}
!30 = distinct !{!30, !29}
!31 = !{!7, !3, i64 28}
!32 = !{!7, !3, i64 116}
!33 = !{!7, !8, i64 136}
!34 = !{!7, !8, i64 128}
!35 = !{!7, !3, i64 112}
!36 = !{!7, !3, i64 48}
!37 = !{!7, !8, i64 80}
!38 = !{!7, !8, i64 144}
!39 = !{!7, !3, i64 52}
!40 = !{!7, !8, i64 152}
!41 = !{!7, !3, i64 108}
!42 = !{!7, !3, i64 56}
!43 = !{!7, !3, i64 120}
!44 = !{!7, !3, i64 60}
!45 = !{!7, !3, i64 96}
!46 = !{!7, !3, i64 100}
!47 = !{!7, !3, i64 104}
!48 = !{!7, !8, i64 184}
!49 = !{!4, !4, i64 0}
!50 = distinct !{!50, !29}
!51 = !{!3, !3, i64 0}
!52 = distinct !{!52, !29}
