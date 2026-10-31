; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@labels_page_a = external constant [0 x i8], align 1
@labels_page_b = external constant [0 x i8], align 1
@labels_page_c = external constant [0 x i8], align 1
@labels_page_d = external constant [0 x i8], align 1
@switch.table.s4_menu = private unnamed_addr constant [18 x i8] c"\0A\0B\0B\0B\0B\0B\09\08\07\0B\0B\06\05\04\03\02\0B\01", align 4

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %5 = and i32 %4, 1
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %148

7:                                                ; preds = %1
  %8 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %9 = or i32 %8, 1
  store volatile i32 %9, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
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
  br label %10

10:                                               ; preds = %110, %7
  %11 = phi i64 [ %111, %110 ], [ 0, %7 ]
  %12 = icmp eq i64 %11, 16
  br i1 %12, label %13, label %19

13:                                               ; preds = %10
  %14 = call i64 @lv1_hcall(i64 noundef 170, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %15 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %16 = add i32 %15, 1
  store volatile i32 %16, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %17 = trunc i64 %14 to i32
  store volatile i32 %17, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !19
  %18 = icmp eq i64 %14, 0
  br i1 %18, label %113, label %112

19:                                               ; preds = %10
  %20 = or disjoint i64 %11, 7094703231829278720
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %21 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #5
  %22 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %23 = add i32 %22, 1
  store volatile i32 %23, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %24 = icmp eq i64 %21, 0
  br i1 %24, label %30, label %25

25:                                               ; preds = %19
  %26 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %27 = icmp eq i32 %26, 0
  br i1 %27, label %28, label %110

28:                                               ; preds = %25
  %29 = trunc i64 %21 to i32
  store volatile i32 %29, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %110

30:                                               ; preds = %19
  %31 = load i64, ptr %2, align 8, !tbaa !9
  %32 = icmp eq i64 %31, 5
  %33 = trunc i64 %11 to i8
  br i1 %32, label %34, label %35

34:                                               ; preds = %30
  store volatile i8 %33, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !10
  br label %35

35:                                               ; preds = %34, %30
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %36 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #5
  %37 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %38 = add i32 %37, 1
  store volatile i32 %38, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %39 = icmp eq i64 %36, 0
  %40 = load i64, ptr %2, align 8
  %41 = select i1 %39, i64 %40, i64 0
  %42 = icmp eq i64 %11, 4
  br label %43

43:                                               ; preds = %108, %35
  %44 = phi i64 [ %109, %108 ], [ 0, %35 ]
  %45 = icmp eq i64 %44, 16
  br i1 %45, label %110, label %46

46:                                               ; preds = %43
  %47 = or disjoint i64 %44, 7234318118812647424
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %48 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef %47, i64 noundef 8392862959675637760, i64 noundef 0) #5
  %49 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %50 = add i32 %49, 1
  store volatile i32 %50, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %51 = icmp eq i64 %44, 2
  %52 = and i1 %42, %51
  br i1 %52, label %53, label %55

53:                                               ; preds = %46
  %54 = trunc i64 %48 to i32
  store volatile i32 %54, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !21
  br label %55

55:                                               ; preds = %53, %46
  %56 = icmp eq i64 %48, 0
  br i1 %56, label %57, label %108

57:                                               ; preds = %55
  %58 = load i64, ptr %2, align 8, !tbaa !9
  %59 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %60 = add i32 %59, 1
  store volatile i32 %60, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %61 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef %47, i64 noundef 7594194871653498880, i64 noundef 0) #5
  %62 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %63 = add i32 %62, 1
  store volatile i32 %63, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %64 = icmp eq i64 %61, 0
  %65 = load i64, ptr %2, align 8
  %66 = select i1 %64, i64 %65, i64 0
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %67 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef %47, i64 noundef 8101820097204584448, i64 noundef 0) #5
  %68 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %69 = add i32 %68, 1
  store volatile i32 %69, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %70 = icmp eq i64 %67, 0
  %71 = load i64, ptr %2, align 8
  %72 = trunc i64 %71 to i32
  %73 = select i1 %70, i32 %72, i32 255
  %74 = icmp eq i64 %58, 5
  br i1 %74, label %75, label %98

75:                                               ; preds = %57
  %76 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %77 = add i32 %76, 1
  store volatile i32 %77, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %78 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %79 = icmp eq i32 %78, 1
  br i1 %79, label %80, label %90

80:                                               ; preds = %75
  store volatile i8 %33, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %81 = trunc i64 %44 to i8
  store volatile i8 %81, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %82 = trunc i32 %73 to i8
  store volatile i8 %82, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  store volatile i64 %41, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !24
  store volatile i64 %66, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !25
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %83 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %20, i64 noundef %47, i64 noundef 8243108395510267904, i64 noundef 7594194871653498880) #5
  %84 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %85 = add i32 %84, 1
  store volatile i32 %85, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %86 = icmp eq i64 %83, 0
  br i1 %86, label %87, label %90

87:                                               ; preds = %80
  %88 = load i64, ptr %2, align 8, !tbaa !9
  %89 = trunc i64 %88 to i32
  store volatile i32 %89, ptr inttoptr (i64 9637788 to ptr), align 4, !tbaa !17
  br label %90

90:                                               ; preds = %87, %80, %75
  br i1 %32, label %91, label %94

91:                                               ; preds = %90
  %92 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %93 = or i8 %92, 1
  store volatile i8 %93, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  br label %94

94:                                               ; preds = %91, %90
  br i1 %42, label %95, label %108

95:                                               ; preds = %94
  %96 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %97 = or i8 %96, 2
  store volatile i8 %97, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  br label %108

98:                                               ; preds = %57
  %99 = icmp eq i64 %58, 0
  %100 = select i1 %42, i1 %99, i1 false
  %101 = icmp eq i32 %73, 2
  %102 = select i1 %100, i1 %101, i1 false
  br i1 %102, label %103, label %108

103:                                              ; preds = %98
  %104 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %105 = icmp eq i32 %104, 0
  br i1 %105, label %106, label %108

106:                                              ; preds = %103
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  store volatile i8 4, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %107 = trunc i64 %44 to i8
  store volatile i8 %107, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  store volatile i8 2, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  br label %108

108:                                              ; preds = %106, %103, %98, %95, %94, %55
  %109 = add nuw nsw i64 %44, 1
  br label %43, !llvm.loop !28

110:                                              ; preds = %43, %28, %25
  %111 = add nuw nsw i64 %11, 1
  br label %10, !llvm.loop !30

112:                                              ; preds = %13
  store volatile i32 1, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %17, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %145

113:                                              ; preds = %13
  %114 = call i64 @lv1_hcall(i64 noundef 174, i64 noundef 4, i64 noundef 2, i64 noundef 524288, i64 noundef 12, i64 noundef 0, i64 noundef 0) #5
  %115 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %116 = add i32 %115, 1
  store volatile i32 %116, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %117 = trunc i64 %114 to i32
  store volatile i32 %117, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !32
  %118 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !33
  store volatile i64 %118, ptr inttoptr (i64 9637808 to ptr), align 16, !tbaa !34
  %119 = icmp eq i64 %114, 0
  br i1 %119, label %125, label %120

120:                                              ; preds = %113
  store volatile i32 3, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %117, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %121 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %122 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %123 = add i32 %122, 1
  store volatile i32 %123, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %124 = trunc i64 %121 to i32
  store volatile i32 %124, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  br label %145

125:                                              ; preds = %113
  %126 = call i64 @lv1_hcall(i64 noundef 175, i64 noundef 4, i64 noundef 2, i64 noundef %118, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %127 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %128 = add i32 %127, 1
  store volatile i32 %128, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %129 = trunc i64 %126 to i32
  store volatile i32 %129, ptr inttoptr (i64 9637772 to ptr), align 4, !tbaa !36
  %130 = icmp eq i64 %126, 0
  br i1 %130, label %135, label %131

131:                                              ; preds = %125
  %132 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %133 = icmp eq i32 %132, 0
  br i1 %133, label %134, label %135

134:                                              ; preds = %131
  store volatile i32 10, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %129, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %135

135:                                              ; preds = %134, %131, %125
  %136 = call i64 @lv1_hcall(i64 noundef 171, i64 noundef 4, i64 noundef 2, i64 noundef 0, i64 noundef 0, i64 noundef 0, i64 noundef 0) #5
  %137 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %138 = add i32 %137, 1
  store volatile i32 %138, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !18
  %139 = trunc i64 %136 to i32
  store volatile i32 %139, ptr inttoptr (i64 9637776 to ptr), align 16, !tbaa !35
  %140 = icmp eq i64 %136, 0
  br i1 %140, label %145, label %141

141:                                              ; preds = %135
  %142 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %143 = icmp eq i32 %142, 0
  br i1 %143, label %144, label %145

144:                                              ; preds = %141
  store volatile i32 11, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  store volatile i32 %139, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %145

145:                                              ; preds = %112, %120, %135, %141, %144
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #4
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #4
  %146 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %147 = or i32 %146, 2
  store volatile i32 %147, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %148

148:                                              ; preds = %145, %1
  %149 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %150 = and i32 %149, 2
  %151 = icmp eq i32 %150, 0
  br i1 %151, label %300, label %152

152:                                              ; preds = %148
  %153 = trunc i64 %0 to i32
  %154 = and i32 %153, 3
  switch i32 %154, label %299 [
    i32 0, label %155
    i32 1, label %196
    i32 2, label %220
    i32 3, label %232
  ]

155:                                              ; preds = %152
  %156 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %157 = icmp eq i32 %156, 0
  br i1 %157, label %174, label %158

158:                                              ; preds = %155
  %159 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %160 = and i32 %159, 1
  %161 = icmp eq i32 %160, 0
  br i1 %161, label %162, label %300

162:                                              ; preds = %158
  %163 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %164 = and i32 %163, 2
  %165 = icmp eq i32 %164, 0
  br i1 %165, label %166, label %300

166:                                              ; preds = %162
  %167 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %168 = and i32 %167, 4
  %169 = icmp eq i32 %168, 0
  br i1 %169, label %170, label %300

170:                                              ; preds = %166
  %171 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %172 = and i32 %171, 8
  %173 = icmp eq i32 %172, 0
  br i1 %173, label %174, label %300

174:                                              ; preds = %170, %155
  %175 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %176 = icmp eq i32 %175, 0
  br i1 %176, label %300, label %177

177:                                              ; preds = %174
  %178 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %179 = call i32 @llvm.umin.i32(i32 %178, i32 11)
  %180 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %181 = add i32 %180, 17
  %182 = icmp ult i32 %181, 18
  br i1 %182, label %183, label %188

183:                                              ; preds = %177
  %184 = zext nneg i32 %181 to i64
  %185 = getelementptr inbounds nuw i8, ptr @switch.table.s4_menu, i64 %184
  %186 = load i8, ptr %185, align 1
  %187 = zext i8 %186 to i32
  br label %188

188:                                              ; preds = %177, %183
  %189 = phi i32 [ %187, %183 ], [ 11, %177 ]
  %190 = mul nuw nsw i32 %179, 12
  %191 = add nuw nsw i32 %190, 67108857
  %192 = add nuw nsw i32 %191, %189
  %193 = shl i32 %192, 6
  %194 = zext i32 %193 to i64
  %195 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %194
  br label %300

196:                                              ; preds = %152
  %197 = load volatile i32, ptr inttoptr (i64 9637692 to ptr), align 4, !tbaa !31
  %198 = icmp eq i32 %197, 0
  br i1 %198, label %199, label %202

199:                                              ; preds = %196
  %200 = load volatile i32, ptr inttoptr (i64 9637784 to ptr), align 8, !tbaa !37
  %201 = icmp eq i32 %200, 0
  br i1 %201, label %300, label %202

202:                                              ; preds = %199, %196
  %203 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %204 = icmp ugt i32 %203, -257
  br i1 %204, label %205, label %207

205:                                              ; preds = %202
  %206 = and i32 %203, 255
  br label %214

207:                                              ; preds = %202
  %208 = icmp ult i32 %203, 256
  br i1 %208, label %209, label %211

209:                                              ; preds = %207
  %210 = or disjoint i32 %203, 256
  br label %214

211:                                              ; preds = %207
  %212 = lshr i32 %203, 28
  %213 = or disjoint i32 %212, 512
  br label %214

214:                                              ; preds = %205, %209, %211
  %215 = phi i32 [ %206, %205 ], [ %210, %209 ], [ %213, %211 ]
  %216 = shl nuw nsw i32 %215, 6
  %217 = zext nneg i32 %216 to i64
  %218 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %217
  %219 = getelementptr inbounds nuw i8, ptr %218, i64 64
  br label %300

220:                                              ; preds = %152
  %221 = load volatile i64, ptr inttoptr (i64 9637808 to ptr), align 16, !tbaa !34
  %222 = load volatile i32, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !32
  %223 = icmp eq i32 %222, 0
  br i1 %223, label %224, label %300

224:                                              ; preds = %220
  %225 = and i64 %221, 4294967288
  %226 = icmp eq i64 %225, 0
  br i1 %226, label %227, label %300

227:                                              ; preds = %224
  %228 = shl i64 %221, 6
  %229 = add nuw nsw i64 %228, 64
  %230 = and i64 %229, 960
  %231 = getelementptr inbounds nuw i8, ptr @labels_page_c, i64 %230
  br label %300

232:                                              ; preds = %152
  %233 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !23
  %234 = icmp eq i32 %233, 0
  br i1 %234, label %257, label %235

235:                                              ; preds = %232
  %236 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %237 = icmp eq i8 %236, 4
  br i1 %237, label %238, label %244

238:                                              ; preds = %235
  %239 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %240 = icmp eq i8 %239, 2
  br i1 %240, label %241, label %244

241:                                              ; preds = %238
  %242 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  %243 = icmp eq i8 %242, 0
  br i1 %243, label %257, label %244

244:                                              ; preds = %241, %238, %235
  %245 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %246 = icmp eq i8 %245, 5
  br i1 %246, label %247, label %250

247:                                              ; preds = %244
  %248 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %249 = icmp eq i8 %248, 0
  br i1 %249, label %257, label %250

250:                                              ; preds = %247, %244
  %251 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %252 = icmp eq i8 %251, 4
  br i1 %252, label %253, label %256

253:                                              ; preds = %250
  %254 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %255 = icmp eq i8 %254, 2
  br i1 %255, label %257, label %256

256:                                              ; preds = %253, %250
  br label %257

257:                                              ; preds = %256, %253, %247, %241, %232
  %258 = phi i64 [ 0, %232 ], [ 901, %241 ], [ 1802, %247 ], [ 3604, %256 ], [ 2703, %253 ]
  %259 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !27
  %260 = icmp eq i32 %259, 0
  br i1 %260, label %293, label %261

261:                                              ; preds = %257
  %262 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %263 = icmp ult i8 %262, 8
  br i1 %263, label %264, label %268

264:                                              ; preds = %261
  %265 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %266 = zext i8 %265 to i64
  %267 = mul nuw nsw i64 %266, 5
  br label %268

268:                                              ; preds = %264, %261
  %269 = phi i64 [ %267, %264 ], [ 40, %261 ]
  %270 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %271 = icmp ult i8 %270, 4
  br i1 %271, label %272, label %275

272:                                              ; preds = %268
  %273 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %274 = zext i8 %273 to i64
  br label %275

275:                                              ; preds = %272, %268
  %276 = phi i64 [ %274, %272 ], [ 4, %268 ]
  %277 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %278 = icmp ult i8 %277, 4
  br i1 %278, label %279, label %282

279:                                              ; preds = %275
  %280 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %281 = zext i8 %280 to i64
  br label %282

282:                                              ; preds = %279, %275
  %283 = phi i64 [ %281, %279 ], [ 4, %275 ]
  %284 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !26
  %285 = and i8 %284, 3
  %286 = zext nneg i8 %285 to i64
  %287 = add nuw nsw i64 %276, %269
  %288 = mul nuw nsw i64 %287, 5
  %289 = add nuw nsw i64 %283, %288
  %290 = shl nuw nsw i64 %289, 2
  %291 = or disjoint i64 %290, 1
  %292 = add nuw nsw i64 %291, %286
  br label %293

293:                                              ; preds = %257, %282
  %294 = phi i64 [ %292, %282 ], [ 0, %257 ]
  %295 = add nuw nsw i64 %294, %258
  %296 = shl nuw nsw i64 %295, 6
  %297 = and i64 %296, 4294967232
  %298 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %297
  br label %300

299:                                              ; preds = %152
  unreachable

300:                                              ; preds = %188, %214, %293, %158, %162, %166, %170, %174, %199, %224, %220, %227, %148
  %301 = phi ptr [ inttoptr (i64 3165888 to ptr), %148 ], [ %298, %293 ], [ @labels_page_b, %199 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 64), %158 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 128), %162 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 192), %166 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_a, i64 256), %170 ], [ %195, %188 ], [ @labels_page_a, %174 ], [ %219, %214 ], [ @labels_page_c, %220 ], [ %231, %227 ], [ getelementptr inbounds nuw (i8, ptr @labels_page_c, i64 576), %224 ]
  ret ptr %301
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare i64 @lv1_hcall(i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

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
!32 = !{!7, !3, i64 48}
!33 = !{!7, !8, i64 80}
!34 = !{!7, !8, i64 144}
!35 = !{!7, !3, i64 112}
!36 = !{!7, !3, i64 108}
!37 = !{!7, !3, i64 120}
