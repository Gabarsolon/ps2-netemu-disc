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
  br i1 %8, label %9, label %233

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
  br label %230

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
  br label %229

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
  br label %229

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
  br label %229

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
  br label %229

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
  br label %229

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
  %200 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 524288, i64 noundef 0, i64 noundef 0) #6
  %201 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %202 = add i32 %201, 1
  store volatile i32 %202, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %203 = trunc i64 %200 to i32
  store volatile i32 %203, ptr inttoptr (i64 9637768 to ptr), align 8, !tbaa !45
  %204 = icmp eq i64 %200, 0
  br i1 %204, label %209, label %205

205:                                              ; preds = %199
  %206 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %207 = icmp eq i32 %206, 0
  br i1 %207, label %208, label %209

208:                                              ; preds = %205
  store volatile i32 9, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %203, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %209

209:                                              ; preds = %208, %205, %199
  %210 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %211 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %212 = add i32 %211, 1
  store volatile i32 %212, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %213 = trunc i64 %210 to i32
  store volatile i32 %213, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !41
  %214 = icmp eq i64 %210, 0
  br i1 %214, label %219, label %215

215:                                              ; preds = %209
  %216 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %217 = icmp eq i32 %216, 0
  br i1 %217, label %218, label %219

218:                                              ; preds = %215
  store volatile i32 10, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %213, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %219

219:                                              ; preds = %218, %215, %209
  %220 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #6
  %221 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %222 = add i32 %221, 1
  store volatile i32 %222, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %223 = trunc i64 %220 to i32
  store volatile i32 %223, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  %224 = icmp eq i64 %220, 0
  br i1 %224, label %229, label %225

225:                                              ; preds = %219
  %226 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %227 = icmp eq i32 %226, 0
  br i1 %227, label %228, label %229

228:                                              ; preds = %225
  store volatile i32 11, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %223, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %229

229:                                              ; preds = %228, %225, %219, %188, %174, %151, %138, %126
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #5
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #5
  br label %230

230:                                              ; preds = %114, %229
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #5
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #5
  %231 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %232 = or i32 %231, 2
  store volatile i32 %232, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %233

233:                                              ; preds = %230, %1
  %234 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %235 = and i32 %234, 2
  %236 = icmp eq i32 %235, 0
  br i1 %236, label %412, label %237

237:                                              ; preds = %233
  %238 = trunc i64 %0 to i32
  %239 = and i32 %238, 3
  switch i32 %239, label %411 [
    i32 0, label %240
    i32 1, label %281
    i32 2, label %305
    i32 3, label %344
  ]

240:                                              ; preds = %237
  %241 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %242 = icmp eq i32 %241, 0
  br i1 %242, label %259, label %243

243:                                              ; preds = %240
  %244 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %245 = and i32 %244, 1
  %246 = icmp eq i32 %245, 0
  br i1 %246, label %247, label %412

247:                                              ; preds = %243
  %248 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %249 = and i32 %248, 2
  %250 = icmp eq i32 %249, 0
  br i1 %250, label %251, label %412

251:                                              ; preds = %247
  %252 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %253 = and i32 %252, 4
  %254 = icmp eq i32 %253, 0
  br i1 %254, label %255, label %412

255:                                              ; preds = %251
  %256 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %257 = and i32 %256, 8
  %258 = icmp eq i32 %257, 0
  br i1 %258, label %259, label %412

259:                                              ; preds = %255, %240
  %260 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %261 = icmp eq i32 %260, 0
  br i1 %261, label %412, label %262

262:                                              ; preds = %259
  %263 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %264 = call i32 @llvm.umin.i32(i32 %263, i32 11)
  %265 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %266 = add i32 %265, 17
  %267 = icmp ult i32 %266, 18
  br i1 %267, label %268, label %273

268:                                              ; preds = %262
  %269 = zext nneg i32 %266 to i64
  %270 = getelementptr inbounds nuw i8, ptr @switch.table.s4_menu, i64 %269
  %271 = load i8, ptr %270, align 1
  %272 = zext i8 %271 to i32
  br label %273

273:                                              ; preds = %262, %268
  %274 = phi i32 [ %272, %268 ], [ 11, %262 ]
  %275 = mul nuw nsw i32 %264, 12
  %276 = add nuw nsw i32 %275, 67108857
  %277 = add nuw nsw i32 %276, %274
  %278 = shl i32 %277, 6
  %279 = zext i32 %278 to i64
  %280 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %279
  br label %412

281:                                              ; preds = %237
  %282 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %283 = icmp eq i32 %282, 0
  br i1 %283, label %284, label %287

284:                                              ; preds = %281
  %285 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %286 = icmp eq i32 %285, 0
  br i1 %286, label %412, label %287

287:                                              ; preds = %284, %281
  %288 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %289 = icmp ugt i32 %288, -257
  br i1 %289, label %290, label %292

290:                                              ; preds = %287
  %291 = and i32 %288, 255
  br label %299

292:                                              ; preds = %287
  %293 = icmp ult i32 %288, 256
  br i1 %293, label %294, label %296

294:                                              ; preds = %292
  %295 = or disjoint i32 %288, 256
  br label %299

296:                                              ; preds = %292
  %297 = lshr i32 %288, 28
  %298 = or disjoint i32 %297, 512
  br label %299

299:                                              ; preds = %290, %294, %296
  %300 = phi i32 [ %291, %290 ], [ %295, %294 ], [ %298, %296 ]
  %301 = shl nuw nsw i32 %300, 6
  %302 = zext nneg i32 %301 to i64
  %303 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %302
  %304 = getelementptr inbounds nuw i8, ptr %303, i64 64
  br label %412

305:                                              ; preds = %237
  %306 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %307 = and i32 %306, 1
  %308 = icmp eq i32 %307, 0
  br i1 %308, label %309, label %412

309:                                              ; preds = %305
  %310 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %311 = and i32 %310, 2
  %312 = icmp eq i32 %311, 0
  br i1 %312, label %313, label %412

313:                                              ; preds = %309
  %314 = load volatile i64, ptr inttoptr (i64 9637824 to ptr), align 64, !tbaa !46
  %315 = icmp eq i64 %314, 0
  br i1 %315, label %321, label %316

316:                                              ; preds = %313
  %317 = load volatile i64, ptr inttoptr (i64 9637824 to ptr), align 64, !tbaa !46
  %318 = and i64 %317, 4294967295
  %319 = icmp eq i64 %318, 33700352
  %320 = select i1 %319, ptr getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 128), ptr getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 192)
  br label %412

321:                                              ; preds = %313
  %322 = load volatile i64, ptr inttoptr (i64 9637832 to ptr), align 8, !tbaa !47
  %323 = icmp eq i64 %322, 0
  br i1 %323, label %324, label %412

324:                                              ; preds = %321
  %325 = load volatile i64, ptr inttoptr (i64 9637800 to ptr), align 8, !tbaa !33
  %326 = add i64 %325, 4096
  %327 = inttoptr i64 %326 to ptr
  %328 = getelementptr inbounds nuw i8, ptr %327, i64 8
  %329 = load volatile i8, ptr %328, align 1, !tbaa !48
  %330 = icmp eq i8 %329, 83
  br i1 %330, label %331, label %343

331:                                              ; preds = %324
  %332 = getelementptr inbounds nuw i8, ptr %327, i64 9
  %333 = load volatile i8, ptr %332, align 1, !tbaa !48
  %334 = icmp eq i8 %333, 79
  br i1 %334, label %335, label %343

335:                                              ; preds = %331
  %336 = getelementptr inbounds nuw i8, ptr %327, i64 10
  %337 = load volatile i8, ptr %336, align 1, !tbaa !48
  %338 = icmp eq i8 %337, 78
  br i1 %338, label %339, label %343

339:                                              ; preds = %335
  %340 = getelementptr inbounds nuw i8, ptr %327, i64 11
  %341 = load volatile i8, ptr %340, align 1, !tbaa !48
  %342 = icmp eq i8 %341, 89
  br i1 %342, label %412, label %343

343:                                              ; preds = %339, %335, %331, %324
  br label %412

344:                                              ; preds = %237
  %345 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %346 = icmp eq i32 %345, 0
  br i1 %346, label %369, label %347

347:                                              ; preds = %344
  %348 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %349 = icmp eq i8 %348, 4
  br i1 %349, label %350, label %356

350:                                              ; preds = %347
  %351 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %352 = icmp eq i8 %351, 2
  br i1 %352, label %353, label %356

353:                                              ; preds = %350
  %354 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  %355 = icmp eq i8 %354, 0
  br i1 %355, label %369, label %356

356:                                              ; preds = %353, %350, %347
  %357 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %358 = icmp eq i8 %357, 5
  br i1 %358, label %359, label %362

359:                                              ; preds = %356
  %360 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %361 = icmp eq i8 %360, 0
  br i1 %361, label %369, label %362

362:                                              ; preds = %359, %356
  %363 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %364 = icmp eq i8 %363, 4
  br i1 %364, label %365, label %368

365:                                              ; preds = %362
  %366 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %367 = icmp eq i8 %366, 2
  br i1 %367, label %369, label %368

368:                                              ; preds = %365, %362
  br label %369

369:                                              ; preds = %368, %365, %359, %353, %344
  %370 = phi i64 [ 0, %344 ], [ 901, %353 ], [ 1802, %359 ], [ 3604, %368 ], [ 2703, %365 ]
  %371 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %372 = icmp eq i32 %371, 0
  br i1 %372, label %405, label %373

373:                                              ; preds = %369
  %374 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %375 = icmp ult i8 %374, 8
  br i1 %375, label %376, label %380

376:                                              ; preds = %373
  %377 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %378 = zext i8 %377 to i64
  %379 = mul nuw nsw i64 %378, 5
  br label %380

380:                                              ; preds = %376, %373
  %381 = phi i64 [ %379, %376 ], [ 40, %373 ]
  %382 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %383 = icmp ult i8 %382, 4
  br i1 %383, label %384, label %387

384:                                              ; preds = %380
  %385 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %386 = zext i8 %385 to i64
  br label %387

387:                                              ; preds = %384, %380
  %388 = phi i64 [ %386, %384 ], [ 4, %380 ]
  %389 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %390 = icmp ult i8 %389, 4
  br i1 %390, label %391, label %394

391:                                              ; preds = %387
  %392 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %393 = zext i8 %392 to i64
  br label %394

394:                                              ; preds = %391, %387
  %395 = phi i64 [ %393, %391 ], [ 4, %387 ]
  %396 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %397 = and i8 %396, 3
  %398 = zext nneg i8 %397 to i64
  %399 = add nuw nsw i64 %388, %381
  %400 = mul nuw nsw i64 %399, 5
  %401 = add nuw nsw i64 %395, %400
  %402 = shl nuw nsw i64 %401, 2
  %403 = or disjoint i64 %402, 1
  %404 = add nuw nsw i64 %403, %398
  br label %405

405:                                              ; preds = %369, %394
  %406 = phi i64 [ %404, %394 ], [ 0, %369 ]
  %407 = add nuw nsw i64 %406, %370
  %408 = shl nuw nsw i64 %407, 6
  %409 = and i64 %408, 4294967232
  %410 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %409
  br label %412

411:                                              ; preds = %237
  unreachable

412:                                              ; preds = %273, %299, %405, %243, %247, %251, %255, %259, %284, %305, %309, %316, %321, %339, %343, %233
  %413 = phi ptr [ inttoptr (i64 3165888 to ptr), %233 ], [ %410, %405 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 256), %321 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 64), %243 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 128), %247 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 192), %251 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 256), %255 ], [ %280, %273 ], [ @labels_page_a, %259 ], [ %304, %299 ], [ @labels_page_b, %284 ], [ @labels_page_c, %305 ], [ %320, %316 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 64), %309 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 384), %343 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 320), %339 ]
  ret ptr %413
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
define internal fastcc void @setup_atapi_block(ptr nofree noundef captures(address) %0, i8 noundef zeroext range(i8 0, 19) %1, i32 noundef zeroext range(i32 0, 37) %2, i32 noundef zeroext range(i32 0, 2) %3, i32 noundef zeroext range(i32 0, 2) %4, i64 noundef %5, i32 noundef zeroext range(i32 0, 37) %6) unnamed_addr #3 {
  br label %8

8:                                                ; preds = %13, %7
  %9 = phi i64 [ %15, %13 ], [ 0, %7 ]
  %10 = icmp eq i64 %9, 8
  br i1 %10, label %11, label %13

11:                                               ; preds = %8
  store volatile i8 %1, ptr %0, align 1, !tbaa !48
  %12 = icmp eq i8 %1, 18
  br i1 %12, label %16, label %19

13:                                               ; preds = %8
  %14 = getelementptr inbounds nuw [8 x i8], ptr %0, i64 %9
  store volatile i64 0, ptr %14, align 8, !tbaa !9
  %15 = add nuw nsw i64 %9, 1
  br label %8, !llvm.loop !49

16:                                               ; preds = %11
  %17 = trunc nuw nsw i32 %2 to i8
  %18 = getelementptr inbounds nuw i8, ptr %0, i64 4
  store volatile i8 %17, ptr %18, align 1, !tbaa !48
  br label %19

19:                                               ; preds = %16, %11
  %20 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store volatile i32 12, ptr %20, align 4, !tbaa !50
  %21 = getelementptr inbounds nuw i8, ptr %0, i64 36
  store volatile i32 %2, ptr %21, align 4, !tbaa !50
  %22 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store volatile i32 1, ptr %22, align 4, !tbaa !50
  %23 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store volatile i32 %3, ptr %23, align 4, !tbaa !50
  %24 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store volatile i32 %4, ptr %24, align 4, !tbaa !50
  %25 = getelementptr inbounds nuw i8, ptr %0, i64 56
  store volatile i64 %5, ptr %25, align 8, !tbaa !9
  %26 = getelementptr inbounds nuw i8, ptr %0, i64 64
  store volatile i32 %6, ptr %26, align 8, !tbaa !50
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
  br i1 %16, label %20, label %4, !llvm.loop !51

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
!45 = !{!7, !3, i64 104}
!46 = !{!7, !8, i64 160}
!47 = !{!7, !8, i64 168}
!48 = !{!4, !4, i64 0}
!49 = distinct !{!49, !29}
!50 = !{!3, !3, i64 0}
!51 = distinct !{!51, !29}
