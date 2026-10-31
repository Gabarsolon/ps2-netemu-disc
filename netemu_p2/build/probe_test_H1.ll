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
  br i1 %8, label %9, label %194

9:                                                ; preds = %1
  %10 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %11 = or i32 %10, 1
  store volatile i32 %11, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #4
  store i64 0, ptr %2, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #4
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
  %16 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
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
  %23 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #5
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
  %38 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #5
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
  %50 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8392862959675637760, i64 noundef 0) #5
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
  %63 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 7594194871653498880, i64 noundef 0) #5
  %64 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %65 = add i32 %64, 1
  store volatile i32 %65, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %66 = icmp eq i64 %63, 0
  %67 = load i64, ptr %2, align 8
  %68 = select i1 %66, i64 %67, i64 0
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %69 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8101820097204584448, i64 noundef 0) #5
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
  %85 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8243108395510267904, i64 noundef 7594194871653498880) #5
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
  br label %191

115:                                              ; preds = %15
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #4
  store i64 0, ptr %4, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #4
  store i64 0, ptr %5, align 8, !tbaa !9
  %116 = call i64 @alloc_buffer(ptr noundef nonnull @str_sb_opt, i64 noundef 1048576, ptr noundef nonnull %4, ptr noundef nonnull %5) #5
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
  %127 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %128 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %129 = add i32 %128, 1
  store volatile i32 %129, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %130 = trunc i64 %127 to i32
  store volatile i32 %130, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %190

131:                                              ; preds = %115
  %132 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef 2, i64 noundef 524288, i64 noundef 12, i64 noundef 0, i64 noundef 0) #5
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
  %139 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %140 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %141 = add i32 %140, 1
  store volatile i32 %141, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %142 = trunc i64 %139 to i32
  store volatile i32 %142, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %190

143:                                              ; preds = %131
  %144 = load i64, ptr %5, align 8, !tbaa !9
  %145 = call i64 @lv1_hcall(i64 noundef 176, i64 noundef 4, i64 noundef 2, i64 noundef %144, i64 noundef %136, i64 noundef 524288, i64 noundef -2305843009213691904) #5
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
  %152 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %153 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %154 = add i32 %153, 1
  store volatile i32 %154, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %155 = trunc i64 %152 to i32
  store volatile i32 %155, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !41
  %156 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %157 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %158 = add i32 %157, 1
  store volatile i32 %158, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %159 = trunc i64 %156 to i32
  store volatile i32 %159, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %190

160:                                              ; preds = %143
  %161 = call i64 @lv1_hcall(i64 noundef 177, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 524288, i64 noundef 0, i64 noundef 0) #5
  %162 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %163 = add i32 %162, 1
  store volatile i32 %163, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %164 = trunc i64 %161 to i32
  store volatile i32 %164, ptr inttoptr (i64 9637768 to ptr), align 8, !tbaa !42
  %165 = icmp eq i64 %161, 0
  br i1 %165, label %170, label %166

166:                                              ; preds = %160
  %167 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %168 = icmp eq i32 %167, 0
  br i1 %168, label %169, label %170

169:                                              ; preds = %166
  store volatile i32 9, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %164, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %170

170:                                              ; preds = %169, %166, %160
  %171 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %136, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %172 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %173 = add i32 %172, 1
  store volatile i32 %173, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %174 = trunc i64 %171 to i32
  store volatile i32 %174, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !41
  %175 = icmp eq i64 %171, 0
  br i1 %175, label %180, label %176

176:                                              ; preds = %170
  %177 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %178 = icmp eq i32 %177, 0
  br i1 %178, label %179, label %180

179:                                              ; preds = %176
  store volatile i32 10, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %174, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %180

180:                                              ; preds = %179, %176, %170
  %181 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %182 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %183 = add i32 %182, 1
  store volatile i32 %183, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %184 = trunc i64 %181 to i32
  store volatile i32 %184, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  %185 = icmp eq i64 %181, 0
  br i1 %185, label %190, label %186

186:                                              ; preds = %180
  %187 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %188 = icmp eq i32 %187, 0
  br i1 %188, label %189, label %190

189:                                              ; preds = %186
  store volatile i32 11, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %184, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %190

190:                                              ; preds = %189, %186, %180, %151, %138, %126
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #4
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #4
  br label %191

191:                                              ; preds = %114, %190
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #4
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #4
  %192 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %193 = or i32 %192, 2
  store volatile i32 %193, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %194

194:                                              ; preds = %191, %1
  %195 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %196 = and i32 %195, 2
  %197 = icmp eq i32 %196, 0
  br i1 %197, label %344, label %198

198:                                              ; preds = %194
  %199 = trunc i64 %0 to i32
  %200 = and i32 %199, 3
  switch i32 %200, label %343 [
    i32 0, label %201
    i32 1, label %242
    i32 2, label %266
    i32 3, label %276
  ]

201:                                              ; preds = %198
  %202 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %203 = icmp eq i32 %202, 0
  br i1 %203, label %220, label %204

204:                                              ; preds = %201
  %205 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %206 = and i32 %205, 1
  %207 = icmp eq i32 %206, 0
  br i1 %207, label %208, label %344

208:                                              ; preds = %204
  %209 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %210 = and i32 %209, 2
  %211 = icmp eq i32 %210, 0
  br i1 %211, label %212, label %344

212:                                              ; preds = %208
  %213 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %214 = and i32 %213, 4
  %215 = icmp eq i32 %214, 0
  br i1 %215, label %216, label %344

216:                                              ; preds = %212
  %217 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %218 = and i32 %217, 8
  %219 = icmp eq i32 %218, 0
  br i1 %219, label %220, label %344

220:                                              ; preds = %216, %201
  %221 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %222 = icmp eq i32 %221, 0
  br i1 %222, label %344, label %223

223:                                              ; preds = %220
  %224 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %225 = call i32 @llvm.umin.i32(i32 %224, i32 11)
  %226 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %227 = add i32 %226, 17
  %228 = icmp ult i32 %227, 18
  br i1 %228, label %229, label %234

229:                                              ; preds = %223
  %230 = zext nneg i32 %227 to i64
  %231 = getelementptr inbounds nuw i8, ptr @switch.table.s4_menu, i64 %230
  %232 = load i8, ptr %231, align 1
  %233 = zext i8 %232 to i32
  br label %234

234:                                              ; preds = %223, %229
  %235 = phi i32 [ %233, %229 ], [ 11, %223 ]
  %236 = mul nuw nsw i32 %225, 12
  %237 = add nuw nsw i32 %236, 67108857
  %238 = add nuw nsw i32 %237, %235
  %239 = shl i32 %238, 6
  %240 = zext i32 %239 to i64
  %241 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %240
  br label %344

242:                                              ; preds = %198
  %243 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %244 = icmp eq i32 %243, 0
  br i1 %244, label %245, label %248

245:                                              ; preds = %242
  %246 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !43
  %247 = icmp eq i32 %246, 0
  br i1 %247, label %344, label %248

248:                                              ; preds = %245, %242
  %249 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %250 = icmp ugt i32 %249, -257
  br i1 %250, label %251, label %253

251:                                              ; preds = %248
  %252 = and i32 %249, 255
  br label %260

253:                                              ; preds = %248
  %254 = icmp ult i32 %249, 256
  br i1 %254, label %255, label %257

255:                                              ; preds = %253
  %256 = or disjoint i32 %249, 256
  br label %260

257:                                              ; preds = %253
  %258 = lshr i32 %249, 28
  %259 = or disjoint i32 %258, 512
  br label %260

260:                                              ; preds = %251, %255, %257
  %261 = phi i32 [ %252, %251 ], [ %256, %255 ], [ %259, %257 ]
  %262 = shl nuw nsw i32 %261, 6
  %263 = zext nneg i32 %262 to i64
  %264 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %263
  %265 = getelementptr inbounds nuw i8, ptr %264, i64 64
  br label %344

266:                                              ; preds = %198
  %267 = load volatile i32, ptr inttoptr (i64 9637780 to ptr), align 4, !tbaa !32
  %268 = icmp eq i32 %267, 0
  br i1 %268, label %269, label %344

269:                                              ; preds = %266
  %270 = load volatile i32, ptr inttoptr (i64 9637716 to ptr), align 4, !tbaa !39
  %271 = icmp eq i32 %270, 0
  br i1 %271, label %272, label %344

272:                                              ; preds = %269
  %273 = load volatile i32, ptr inttoptr (i64 9637768 to ptr), align 8, !tbaa !42
  %274 = icmp eq i32 %273, 0
  %275 = select i1 %274, ptr getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 192), ptr getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 128)
  br label %344

276:                                              ; preds = %198
  %277 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %278 = icmp eq i32 %277, 0
  br i1 %278, label %301, label %279

279:                                              ; preds = %276
  %280 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %281 = icmp eq i8 %280, 4
  br i1 %281, label %282, label %288

282:                                              ; preds = %279
  %283 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %284 = icmp eq i8 %283, 2
  br i1 %284, label %285, label %288

285:                                              ; preds = %282
  %286 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  %287 = icmp eq i8 %286, 0
  br i1 %287, label %301, label %288

288:                                              ; preds = %285, %282, %279
  %289 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %290 = icmp eq i8 %289, 5
  br i1 %290, label %291, label %294

291:                                              ; preds = %288
  %292 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %293 = icmp eq i8 %292, 0
  br i1 %293, label %301, label %294

294:                                              ; preds = %291, %288
  %295 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %296 = icmp eq i8 %295, 4
  br i1 %296, label %297, label %300

297:                                              ; preds = %294
  %298 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %299 = icmp eq i8 %298, 2
  br i1 %299, label %301, label %300

300:                                              ; preds = %297, %294
  br label %301

301:                                              ; preds = %300, %297, %291, %285, %276
  %302 = phi i64 [ 0, %276 ], [ 901, %285 ], [ 1802, %291 ], [ 3604, %300 ], [ 2703, %297 ]
  %303 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %304 = icmp eq i32 %303, 0
  br i1 %304, label %337, label %305

305:                                              ; preds = %301
  %306 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %307 = icmp ult i8 %306, 8
  br i1 %307, label %308, label %312

308:                                              ; preds = %305
  %309 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %310 = zext i8 %309 to i64
  %311 = mul nuw nsw i64 %310, 5
  br label %312

312:                                              ; preds = %308, %305
  %313 = phi i64 [ %311, %308 ], [ 40, %305 ]
  %314 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %315 = icmp ult i8 %314, 4
  br i1 %315, label %316, label %319

316:                                              ; preds = %312
  %317 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %318 = zext i8 %317 to i64
  br label %319

319:                                              ; preds = %316, %312
  %320 = phi i64 [ %318, %316 ], [ 4, %312 ]
  %321 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %322 = icmp ult i8 %321, 4
  br i1 %322, label %323, label %326

323:                                              ; preds = %319
  %324 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %325 = zext i8 %324 to i64
  br label %326

326:                                              ; preds = %323, %319
  %327 = phi i64 [ %325, %323 ], [ 4, %319 ]
  %328 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %329 = and i8 %328, 3
  %330 = zext nneg i8 %329 to i64
  %331 = add nuw nsw i64 %320, %313
  %332 = mul nuw nsw i64 %331, 5
  %333 = add nuw nsw i64 %327, %332
  %334 = shl nuw nsw i64 %333, 2
  %335 = or disjoint i64 %334, 1
  %336 = add nuw nsw i64 %335, %330
  br label %337

337:                                              ; preds = %301, %326
  %338 = phi i64 [ %336, %326 ], [ 0, %301 ]
  %339 = add nuw nsw i64 %338, %302
  %340 = shl nuw nsw i64 %339, 6
  %341 = and i64 %340, 4294967232
  %342 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %341
  br label %344

343:                                              ; preds = %198
  unreachable

344:                                              ; preds = %234, %260, %337, %204, %208, %212, %216, %220, %245, %266, %269, %272, %194
  %345 = phi ptr [ inttoptr (i64 3165888 to ptr), %194 ], [ %342, %337 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 64), %269 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 64), %204 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 128), %208 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 192), %212 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 256), %216 ], [ %241, %234 ], [ @labels_page_a, %220 ], [ %265, %260 ], [ @labels_page_b, %245 ], [ @labels_page_c, %266 ], [ %275, %272 ]
  ret ptr %345
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

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #3

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #3 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { nounwind }
attributes #5 = { minsize nobuiltin nounwind optsize "no-builtins" }

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
!42 = !{!7, !3, i64 104}
!43 = !{!7, !3, i64 120}
