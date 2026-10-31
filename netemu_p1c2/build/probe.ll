; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@labels_page_00 = external constant [0 x i8], align 1
@labels_page_01 = external constant [0 x i8], align 1
@labels_page_02 = external constant [0 x i8], align 1
@labels_page_03 = external constant [0 x i8], align 1
@labels_page_04 = external constant [0 x i8], align 1
@labels_page_05 = external constant [0 x i8], align 1
@labels_page_06 = external constant [0 x i8], align 1
@labels_page_07 = external constant [0 x i8], align 1
@labels_page_08 = external constant [0 x i8], align 1
@labels_page_09 = external constant [0 x i8], align 1
@labels_page_10 = external constant [0 x i8], align 1
@labels_page_11 = external constant [0 x i8], align 1
@labels_page_12 = external constant [0 x i8], align 1
@labels_page_13 = external constant [0 x i8], align 1
@labels_page_14 = external constant [0 x i8], align 1
@labels_page_15 = external constant [0 x i8], align 1
@labels_page_16 = external constant [0 x i8], align 1
@labels_page_17 = external constant [0 x i8], align 1
@labels_page_18 = external constant [0 x i8], align 1
@labels_page_19 = external constant [0 x i8], align 1
@labels_page_20 = external constant [0 x i8], align 1
@labels_page_21 = external constant [0 x i8], align 1
@labels_page_22 = external constant [0 x i8], align 1
@labels_page_23 = external constant [0 x i8], align 1

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %5 = and i32 %4, 1
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %136

7:                                                ; preds = %1
  %8 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %9 = or i32 %8, 1
  store volatile i32 %9, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #6
  store i64 0, ptr %2, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #6
  store i64 0, ptr %3, align 8, !tbaa !9
  store volatile i8 -1, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  store volatile i8 -1, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  store volatile i8 -1, ptr inttoptr (i64 9637706 to ptr), align 2, !tbaa !12
  store volatile i8 -1, ptr inttoptr (i64 9637707 to ptr), align 1, !tbaa !13
  store volatile i8 -1, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !14
  store volatile i8 -1, ptr inttoptr (i64 9637709 to ptr), align 1, !tbaa !15
  store volatile i32 0, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !16
  store volatile i64 0, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !17
  %10 = tail call i64 @native_alloc(i64 noundef 4096, i64 noundef 3, i64 noundef 0) #7
  %11 = tail call fastcc signext i32 @arena_rw(i64 noundef %10) #8
  %12 = icmp eq i32 %11, 0
  br i1 %12, label %13, label %16

13:                                               ; preds = %7
  %14 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %15 = or i32 %14, 8
  store volatile i32 %15, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %133

16:                                               ; preds = %7
  %17 = inttoptr i64 %10 to ptr
  br label %18

18:                                               ; preds = %24, %16
  %19 = phi i64 [ %26, %24 ], [ 0, %16 ]
  %20 = icmp eq i64 %19, 4096
  br i1 %20, label %21, label %24

21:                                               ; preds = %18
  store volatile i64 %10, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !18
  %22 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %23 = or i32 %22, 4
  store volatile i32 %23, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %27

24:                                               ; preds = %18
  %25 = getelementptr inbounds nuw i8, ptr %17, i64 %19
  store volatile i8 0, ptr %25, align 1, !tbaa !19
  %26 = add nuw nsw i64 %19, 1
  br label %18, !llvm.loop !20

27:                                               ; preds = %101, %21
  %28 = phi i64 [ %102, %101 ], [ 0, %21 ]
  %29 = icmp eq i64 %28, 16
  br i1 %29, label %30, label %33

30:                                               ; preds = %27
  %31 = load volatile i8, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  %32 = icmp eq i8 %31, -1
  br i1 %32, label %106, label %103

33:                                               ; preds = %27
  %34 = or disjoint i64 %28, 7094703231829278720
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %35 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %34, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #7
  %36 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %37 = add i32 %36, 1
  store volatile i32 %37, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %38 = icmp eq i64 %35, 0
  br i1 %38, label %44, label %39

39:                                               ; preds = %33
  %40 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !23
  %41 = icmp eq i32 %40, 0
  br i1 %41, label %42, label %101

42:                                               ; preds = %39
  %43 = trunc i64 %35 to i32
  store volatile i32 %43, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !23
  br label %101

44:                                               ; preds = %33
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %45 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %34, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #7
  %46 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %47 = add i32 %46, 1
  store volatile i32 %47, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %48 = icmp eq i64 %45, 0
  %49 = load i64, ptr %2, align 8
  %50 = select i1 %48, i64 %49, i64 0
  %51 = icmp eq i64 %28, 4
  %52 = trunc i64 %28 to i8
  br label %53

53:                                               ; preds = %99, %44
  %54 = phi i64 [ %100, %99 ], [ 0, %44 ]
  %55 = icmp eq i64 %54, 16
  br i1 %55, label %101, label %56

56:                                               ; preds = %53
  %57 = or disjoint i64 %54, 7234318118812647424
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %58 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %34, i64 noundef %57, i64 noundef 8392862959675637760, i64 noundef 0) #7
  %59 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %60 = add i32 %59, 1
  store volatile i32 %60, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %61 = icmp eq i64 %58, 0
  br i1 %61, label %62, label %99

62:                                               ; preds = %56
  %63 = load i64, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %64 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %34, i64 noundef %57, i64 noundef 7594194871653498880, i64 noundef 0) #7
  %65 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %66 = add i32 %65, 1
  store volatile i32 %66, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %67 = icmp eq i64 %64, 0
  %68 = load i64, ptr %2, align 8
  %69 = select i1 %67, i64 %68, i64 0
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %70 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %34, i64 noundef %57, i64 noundef 8101820097204584448, i64 noundef 0) #7
  %71 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %72 = add i32 %71, 1
  store volatile i32 %72, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %73 = icmp eq i64 %70, 0
  %74 = load i64, ptr %2, align 8
  %75 = trunc i64 %74 to i32
  %76 = select i1 %73, i32 %75, i32 255
  %77 = icmp eq i64 %63, 5
  br i1 %77, label %78, label %86

78:                                               ; preds = %62
  %79 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !24
  %80 = add i32 %79, 1
  store volatile i32 %80, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !24
  %81 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !24
  %82 = icmp eq i32 %81, 1
  br i1 %82, label %83, label %99

83:                                               ; preds = %78
  store volatile i8 %52, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  %84 = trunc i64 %54 to i8
  store volatile i8 %84, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  %85 = trunc i32 %76 to i8
  store volatile i8 %85, ptr inttoptr (i64 9637706 to ptr), align 2, !tbaa !12
  br label %96

86:                                               ; preds = %62
  %87 = icmp eq i64 %63, 0
  %88 = select i1 %51, i1 %87, i1 false
  %89 = icmp eq i32 %76, 2
  %90 = select i1 %88, i1 %89, i1 false
  br i1 %90, label %91, label %99

91:                                               ; preds = %86
  %92 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !25
  %93 = icmp eq i32 %92, 0
  br i1 %93, label %94, label %99

94:                                               ; preds = %91
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !25
  store volatile i8 4, ptr inttoptr (i64 9637707 to ptr), align 1, !tbaa !13
  %95 = trunc i64 %54 to i8
  store volatile i8 %95, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !14
  store volatile i8 2, ptr inttoptr (i64 9637709 to ptr), align 1, !tbaa !15
  br label %96

96:                                               ; preds = %94, %83
  %97 = phi ptr [ inttoptr (i64 9637712 to ptr), %83 ], [ inttoptr (i64 9637728 to ptr), %94 ]
  %98 = phi ptr [ inttoptr (i64 9637720 to ptr), %83 ], [ inttoptr (i64 9637736 to ptr), %94 ]
  store volatile i64 %50, ptr %97, align 16, !tbaa !9
  store volatile i64 %69, ptr %98, align 8, !tbaa !9
  br label %99

99:                                               ; preds = %96, %91, %86, %78, %56
  %100 = add nuw nsw i64 %54, 1
  br label %53, !llvm.loop !26

101:                                              ; preds = %53, %42, %39
  %102 = add nuw nsw i64 %28, 1
  br label %27, !llvm.loop !27

103:                                              ; preds = %30
  %104 = load volatile i8, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  %105 = zext i8 %104 to i32
  br label %106

106:                                              ; preds = %103, %30
  %107 = phi i32 [ %105, %103 ], [ 4, %30 ]
  %108 = load volatile i8, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  %109 = icmp eq i8 %108, -1
  br i1 %109, label %113, label %110

110:                                              ; preds = %106
  %111 = load volatile i8, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  %112 = zext i8 %111 to i32
  br label %113

113:                                              ; preds = %110, %106
  %114 = phi i32 [ %112, %110 ], [ 2, %106 ]
  call fastcc void @dump_node(ptr noundef %17, i32 noundef zeroext %107, i32 noundef zeroext %114) #8
  %115 = load volatile i8, ptr inttoptr (i64 9637707 to ptr), align 1, !tbaa !13
  %116 = icmp eq i8 %115, -1
  br i1 %116, label %120, label %117

117:                                              ; preds = %113
  %118 = load volatile i8, ptr inttoptr (i64 9637707 to ptr), align 1, !tbaa !13
  %119 = zext i8 %118 to i32
  br label %120

120:                                              ; preds = %117, %113
  %121 = phi i32 [ %119, %117 ], [ 4, %113 ]
  %122 = load volatile i8, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !14
  %123 = icmp eq i8 %122, -1
  br i1 %123, label %127, label %124

124:                                              ; preds = %120
  %125 = load volatile i8, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !14
  %126 = zext i8 %125 to i32
  br label %127

127:                                              ; preds = %124, %120
  %128 = phi i32 [ %126, %124 ], [ 3, %120 ]
  %129 = getelementptr inbounds nuw i8, ptr %17, i64 480
  call fastcc void @dump_node(ptr noundef nonnull %129, i32 noundef zeroext %121, i32 noundef zeroext %128) #8
  %130 = getelementptr inbounds nuw i8, ptr %17, i64 960
  call fastcc void @read_one_field(ptr noundef nonnull %130, i64 noundef 7094703231829278724, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #8
  %131 = getelementptr inbounds nuw i8, ptr %17, i64 984
  call fastcc void @read_one_field(ptr noundef nonnull %131, i64 noundef 7094703231829278724, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #8
  %132 = getelementptr inbounds nuw i8, ptr %17, i64 1008
  call fastcc void @read_one_field(ptr noundef nonnull %132, i64 noundef 7094703231829278724, i64 noundef 7959388172920911360, i64 noundef 0, i64 noundef 0) #8
  br label %133

133:                                              ; preds = %13, %127
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #6
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #6
  %134 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %135 = or i32 %134, 2
  store volatile i32 %135, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %136

136:                                              ; preds = %133, %1
  %137 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %138 = and i32 %137, 8
  %139 = icmp eq i32 %138, 0
  br i1 %139, label %140, label %433

140:                                              ; preds = %136
  %141 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %142 = and i32 %141, 2
  %143 = icmp eq i32 %142, 0
  br i1 %143, label %433, label %144

144:                                              ; preds = %140
  %145 = call fastcc ptr @get_arena() #8
  %146 = icmp eq ptr %145, null
  br i1 %146, label %433, label %147

147:                                              ; preds = %144
  %148 = call i64 @native_clock() #7
  %149 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !17
  %150 = icmp ne i64 %149, 0
  %151 = icmp ugt i64 %148, %149
  %152 = select i1 %150, i1 %151, i1 false
  %153 = sub nuw i64 %148, %149
  %154 = icmp ugt i64 %153, 119700000
  %155 = select i1 %152, i1 %154, i1 false
  br i1 %155, label %156, label %159

156:                                              ; preds = %147
  %157 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !16
  %158 = add i32 %157, 1
  store volatile i32 %158, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !16
  br label %159

159:                                              ; preds = %156, %147
  store volatile i64 %148, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !17
  %160 = call i64 @llvm.umin.i64(i64 %0, i64 8)
  %161 = trunc nuw nsw i64 %160 to i32
  %162 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !16
  %163 = mul i32 %162, 9
  %164 = add i32 %163, %161
  %165 = urem i32 %164, 24
  switch i32 %165, label %432 [
    i32 0, label %166
    i32 1, label %226
    i32 2, label %234
    i32 3, label %243
    i32 4, label %252
    i32 5, label %261
    i32 6, label %270
    i32 7, label %279
    i32 8, label %288
    i32 9, label %297
    i32 10, label %306
    i32 11, label %315
    i32 12, label %324
    i32 13, label %333
    i32 14, label %342
    i32 15, label %351
    i32 16, label %360
    i32 17, label %369
    i32 18, label %378
    i32 19, label %387
    i32 20, label %396
    i32 21, label %405
    i32 22, label %414
    i32 23, label %423
  ]

166:                                              ; preds = %159
  %167 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !24
  %168 = icmp ugt i32 %167, 4
  br i1 %168, label %172, label %169

169:                                              ; preds = %166
  %170 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !24
  %171 = shl i32 %170, 1
  br label %172

172:                                              ; preds = %166, %169
  %173 = phi i32 [ %171, %169 ], [ 8, %166 ]
  %174 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !25
  %175 = icmp ne i32 %174, 0
  %176 = zext i1 %175 to i32
  %177 = load volatile i8, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  %178 = icmp ugt i8 %177, 15
  br i1 %178, label %182, label %179

179:                                              ; preds = %172
  %180 = load volatile i8, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !10
  %181 = zext i8 %180 to i64
  br label %182

182:                                              ; preds = %172, %179
  %183 = phi i64 [ %181, %179 ], [ 15, %172 ]
  %184 = load volatile i8, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  %185 = icmp ugt i8 %184, 15
  br i1 %185, label %189, label %186

186:                                              ; preds = %182
  %187 = load volatile i8, ptr inttoptr (i64 9637705 to ptr), align 1, !tbaa !11
  %188 = zext i8 %187 to i64
  br label %189

189:                                              ; preds = %182, %186
  %190 = phi i64 [ %188, %186 ], [ 15, %182 ]
  %191 = load volatile i8, ptr inttoptr (i64 9637706 to ptr), align 2, !tbaa !12
  %192 = icmp ult i8 %191, 3
  br i1 %192, label %193, label %196

193:                                              ; preds = %189
  %194 = load volatile i8, ptr inttoptr (i64 9637706 to ptr), align 2, !tbaa !12
  %195 = zext i8 %194 to i32
  br label %196

196:                                              ; preds = %189, %193
  %197 = phi i32 [ %195, %193 ], [ 3, %189 ]
  %198 = load volatile i64, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !28
  %199 = icmp eq i64 %198, 4
  br i1 %199, label %200, label %203

200:                                              ; preds = %196
  %201 = load volatile i64, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !29
  %202 = icmp eq i64 %201, 2
  br i1 %202, label %216, label %203

203:                                              ; preds = %200, %196
  %204 = load volatile i64, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !28
  %205 = icmp eq i64 %204, %183
  br i1 %205, label %206, label %209

206:                                              ; preds = %203
  %207 = load volatile i64, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !29
  %208 = icmp eq i64 %207, %190
  br i1 %208, label %216, label %209

209:                                              ; preds = %206, %203
  %210 = load volatile i64, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !28
  %211 = icmp eq i64 %210, 1280
  br i1 %211, label %212, label %215

212:                                              ; preds = %209
  %213 = load volatile i64, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !29
  %214 = icmp eq i64 %213, 1281
  br i1 %214, label %216, label %215

215:                                              ; preds = %212, %209
  br label %216

216:                                              ; preds = %212, %206, %200, %215
  %217 = phi i32 [ 12, %215 ], [ 0, %200 ], [ 4, %206 ], [ 8, %212 ]
  %218 = or disjoint i32 %173, %176
  %219 = shl i32 %218, 4
  %220 = add i32 %197, %219
  %221 = add i32 %220, %217
  %222 = call i32 @llvm.umin.i32(i32 %221, i32 159)
  %223 = shl nuw nsw i32 %222, 5
  %224 = zext nneg i32 %223 to i64
  %225 = getelementptr inbounds nuw i8, ptr @labels_page_00, i64 %224
  br label %433

226:                                              ; preds = %159
  %227 = load volatile i64, ptr %145, align 8, !tbaa !30
  %228 = getelementptr inbounds nuw i8, ptr %145, i64 8
  %229 = load volatile i64, ptr %228, align 8, !tbaa !32
  %230 = call fastcc zeroext i32 @map_field_idx(i64 noundef %227, i64 noundef %229) #8
  %231 = shl nuw nsw i32 %230, 5
  %232 = zext nneg i32 %231 to i64
  %233 = getelementptr inbounds nuw i8, ptr @labels_page_01, i64 %232
  br label %433

234:                                              ; preds = %159
  %235 = getelementptr inbounds nuw i8, ptr %145, i64 480
  %236 = load volatile i64, ptr %235, align 8, !tbaa !30
  %237 = getelementptr inbounds nuw i8, ptr %145, i64 488
  %238 = load volatile i64, ptr %237, align 8, !tbaa !32
  %239 = call fastcc zeroext i32 @map_field_idx(i64 noundef %236, i64 noundef %238) #8
  %240 = shl nuw nsw i32 %239, 5
  %241 = zext nneg i32 %240 to i64
  %242 = getelementptr inbounds nuw i8, ptr @labels_page_02, i64 %241
  br label %433

243:                                              ; preds = %159
  %244 = getelementptr inbounds nuw i8, ptr %145, i64 24
  %245 = load volatile i64, ptr %244, align 8, !tbaa !30
  %246 = getelementptr inbounds nuw i8, ptr %145, i64 32
  %247 = load volatile i64, ptr %246, align 8, !tbaa !32
  %248 = call fastcc zeroext i32 @map_field_idx(i64 noundef %245, i64 noundef %247) #8
  %249 = shl nuw nsw i32 %248, 5
  %250 = zext nneg i32 %249 to i64
  %251 = getelementptr inbounds nuw i8, ptr @labels_page_03, i64 %250
  br label %433

252:                                              ; preds = %159
  %253 = getelementptr inbounds nuw i8, ptr %145, i64 504
  %254 = load volatile i64, ptr %253, align 8, !tbaa !30
  %255 = getelementptr inbounds nuw i8, ptr %145, i64 512
  %256 = load volatile i64, ptr %255, align 8, !tbaa !32
  %257 = call fastcc zeroext i32 @map_field_idx(i64 noundef %254, i64 noundef %256) #8
  %258 = shl nuw nsw i32 %257, 5
  %259 = zext nneg i32 %258 to i64
  %260 = getelementptr inbounds nuw i8, ptr @labels_page_04, i64 %259
  br label %433

261:                                              ; preds = %159
  %262 = getelementptr inbounds nuw i8, ptr %145, i64 48
  %263 = load volatile i64, ptr %262, align 8, !tbaa !30
  %264 = getelementptr inbounds nuw i8, ptr %145, i64 56
  %265 = load volatile i64, ptr %264, align 8, !tbaa !32
  %266 = call fastcc zeroext i32 @map_field_idx(i64 noundef %263, i64 noundef %265) #8
  %267 = shl nuw nsw i32 %266, 5
  %268 = zext nneg i32 %267 to i64
  %269 = getelementptr inbounds nuw i8, ptr @labels_page_05, i64 %268
  br label %433

270:                                              ; preds = %159
  %271 = getelementptr inbounds nuw i8, ptr %145, i64 528
  %272 = load volatile i64, ptr %271, align 8, !tbaa !30
  %273 = getelementptr inbounds nuw i8, ptr %145, i64 536
  %274 = load volatile i64, ptr %273, align 8, !tbaa !32
  %275 = call fastcc zeroext i32 @map_field_idx(i64 noundef %272, i64 noundef %274) #8
  %276 = shl nuw nsw i32 %275, 5
  %277 = zext nneg i32 %276 to i64
  %278 = getelementptr inbounds nuw i8, ptr @labels_page_06, i64 %277
  br label %433

279:                                              ; preds = %159
  %280 = getelementptr inbounds nuw i8, ptr %145, i64 72
  %281 = load volatile i64, ptr %280, align 8, !tbaa !30
  %282 = getelementptr inbounds nuw i8, ptr %145, i64 80
  %283 = load volatile i64, ptr %282, align 8, !tbaa !32
  %284 = call fastcc zeroext i32 @map_blk_idx(i64 noundef %281, i64 noundef %283) #8
  %285 = shl nuw nsw i32 %284, 5
  %286 = zext nneg i32 %285 to i64
  %287 = getelementptr inbounds nuw i8, ptr @labels_page_07, i64 %286
  br label %433

288:                                              ; preds = %159
  %289 = getelementptr inbounds nuw i8, ptr %145, i64 552
  %290 = load volatile i64, ptr %289, align 8, !tbaa !30
  %291 = getelementptr inbounds nuw i8, ptr %145, i64 560
  %292 = load volatile i64, ptr %291, align 8, !tbaa !32
  %293 = call fastcc zeroext i32 @map_blk_idx(i64 noundef %290, i64 noundef %292) #8
  %294 = shl nuw nsw i32 %293, 5
  %295 = zext nneg i32 %294 to i64
  %296 = getelementptr inbounds nuw i8, ptr @labels_page_08, i64 %295
  br label %433

297:                                              ; preds = %159
  %298 = getelementptr inbounds nuw i8, ptr %145, i64 96
  %299 = load volatile i64, ptr %298, align 8, !tbaa !30
  %300 = getelementptr inbounds nuw i8, ptr %145, i64 104
  %301 = load volatile i64, ptr %300, align 8, !tbaa !32
  %302 = call fastcc zeroext i32 @map_field_idx(i64 noundef %299, i64 noundef %301) #8
  %303 = shl nuw nsw i32 %302, 5
  %304 = zext nneg i32 %303 to i64
  %305 = getelementptr inbounds nuw i8, ptr @labels_page_09, i64 %304
  br label %433

306:                                              ; preds = %159
  %307 = getelementptr inbounds nuw i8, ptr %145, i64 576
  %308 = load volatile i64, ptr %307, align 8, !tbaa !30
  %309 = getelementptr inbounds nuw i8, ptr %145, i64 584
  %310 = load volatile i64, ptr %309, align 8, !tbaa !32
  %311 = call fastcc zeroext i32 @map_field_idx(i64 noundef %308, i64 noundef %310) #8
  %312 = shl nuw nsw i32 %311, 5
  %313 = zext nneg i32 %312 to i64
  %314 = getelementptr inbounds nuw i8, ptr @labels_page_10, i64 %313
  br label %433

315:                                              ; preds = %159
  %316 = getelementptr inbounds nuw i8, ptr %145, i64 120
  %317 = load volatile i64, ptr %316, align 8, !tbaa !30
  %318 = getelementptr inbounds nuw i8, ptr %145, i64 128
  %319 = load volatile i64, ptr %318, align 8, !tbaa !32
  %320 = call fastcc zeroext i32 @map_field_idx(i64 noundef %317, i64 noundef %319) #8
  %321 = shl nuw nsw i32 %320, 5
  %322 = zext nneg i32 %321 to i64
  %323 = getelementptr inbounds nuw i8, ptr @labels_page_11, i64 %322
  br label %433

324:                                              ; preds = %159
  %325 = getelementptr inbounds nuw i8, ptr %145, i64 600
  %326 = load volatile i64, ptr %325, align 8, !tbaa !30
  %327 = getelementptr inbounds nuw i8, ptr %145, i64 608
  %328 = load volatile i64, ptr %327, align 8, !tbaa !32
  %329 = call fastcc zeroext i32 @map_field_idx(i64 noundef %326, i64 noundef %328) #8
  %330 = shl nuw nsw i32 %329, 5
  %331 = zext nneg i32 %330 to i64
  %332 = getelementptr inbounds nuw i8, ptr @labels_page_12, i64 %331
  br label %433

333:                                              ; preds = %159
  %334 = getelementptr inbounds nuw i8, ptr %145, i64 144
  %335 = load volatile i64, ptr %334, align 8, !tbaa !30
  %336 = getelementptr inbounds nuw i8, ptr %145, i64 152
  %337 = load volatile i64, ptr %336, align 8, !tbaa !32
  %338 = call fastcc zeroext i32 @map_field_idx(i64 noundef %335, i64 noundef %337) #8
  %339 = shl nuw nsw i32 %338, 5
  %340 = zext nneg i32 %339 to i64
  %341 = getelementptr inbounds nuw i8, ptr @labels_page_13, i64 %340
  br label %433

342:                                              ; preds = %159
  %343 = getelementptr inbounds nuw i8, ptr %145, i64 624
  %344 = load volatile i64, ptr %343, align 8, !tbaa !30
  %345 = getelementptr inbounds nuw i8, ptr %145, i64 632
  %346 = load volatile i64, ptr %345, align 8, !tbaa !32
  %347 = call fastcc zeroext i32 @map_field_idx(i64 noundef %344, i64 noundef %346) #8
  %348 = shl nuw nsw i32 %347, 5
  %349 = zext nneg i32 %348 to i64
  %350 = getelementptr inbounds nuw i8, ptr @labels_page_14, i64 %349
  br label %433

351:                                              ; preds = %159
  %352 = getelementptr inbounds nuw i8, ptr %145, i64 168
  %353 = load volatile i64, ptr %352, align 8, !tbaa !30
  %354 = getelementptr inbounds nuw i8, ptr %145, i64 176
  %355 = load volatile i64, ptr %354, align 8, !tbaa !32
  %356 = call fastcc zeroext i32 @map_field_idx(i64 noundef %353, i64 noundef %355) #8
  %357 = shl nuw nsw i32 %356, 5
  %358 = zext nneg i32 %357 to i64
  %359 = getelementptr inbounds nuw i8, ptr @labels_page_15, i64 %358
  br label %433

360:                                              ; preds = %159
  %361 = getelementptr inbounds nuw i8, ptr %145, i64 648
  %362 = load volatile i64, ptr %361, align 8, !tbaa !30
  %363 = getelementptr inbounds nuw i8, ptr %145, i64 656
  %364 = load volatile i64, ptr %363, align 8, !tbaa !32
  %365 = call fastcc zeroext i32 @map_field_idx(i64 noundef %362, i64 noundef %364) #8
  %366 = shl nuw nsw i32 %365, 5
  %367 = zext nneg i32 %366 to i64
  %368 = getelementptr inbounds nuw i8, ptr @labels_page_16, i64 %367
  br label %433

369:                                              ; preds = %159
  %370 = getelementptr inbounds nuw i8, ptr %145, i64 240
  %371 = load volatile i64, ptr %370, align 8, !tbaa !30
  %372 = getelementptr inbounds nuw i8, ptr %145, i64 248
  %373 = load volatile i64, ptr %372, align 8, !tbaa !32
  %374 = call fastcc zeroext i32 @map_field_idx(i64 noundef %371, i64 noundef %373) #8
  %375 = shl nuw nsw i32 %374, 5
  %376 = zext nneg i32 %375 to i64
  %377 = getelementptr inbounds nuw i8, ptr @labels_page_17, i64 %376
  br label %433

378:                                              ; preds = %159
  %379 = getelementptr inbounds nuw i8, ptr %145, i64 720
  %380 = load volatile i64, ptr %379, align 8, !tbaa !30
  %381 = getelementptr inbounds nuw i8, ptr %145, i64 728
  %382 = load volatile i64, ptr %381, align 8, !tbaa !32
  %383 = call fastcc zeroext i32 @map_field_idx(i64 noundef %380, i64 noundef %382) #8
  %384 = shl nuw nsw i32 %383, 5
  %385 = zext nneg i32 %384 to i64
  %386 = getelementptr inbounds nuw i8, ptr @labels_page_18, i64 %385
  br label %433

387:                                              ; preds = %159
  %388 = getelementptr inbounds nuw i8, ptr %145, i64 336
  %389 = load volatile i64, ptr %388, align 8, !tbaa !30
  %390 = getelementptr inbounds nuw i8, ptr %145, i64 344
  %391 = load volatile i64, ptr %390, align 8, !tbaa !32
  %392 = call fastcc zeroext i32 @map_field_idx(i64 noundef %389, i64 noundef %391) #8
  %393 = shl nuw nsw i32 %392, 5
  %394 = zext nneg i32 %393 to i64
  %395 = getelementptr inbounds nuw i8, ptr @labels_page_19, i64 %394
  br label %433

396:                                              ; preds = %159
  %397 = getelementptr inbounds nuw i8, ptr %145, i64 816
  %398 = load volatile i64, ptr %397, align 8, !tbaa !30
  %399 = getelementptr inbounds nuw i8, ptr %145, i64 824
  %400 = load volatile i64, ptr %399, align 8, !tbaa !32
  %401 = call fastcc zeroext i32 @map_field_idx(i64 noundef %398, i64 noundef %400) #8
  %402 = shl nuw nsw i32 %401, 5
  %403 = zext nneg i32 %402 to i64
  %404 = getelementptr inbounds nuw i8, ptr @labels_page_20, i64 %403
  br label %433

405:                                              ; preds = %159
  %406 = getelementptr inbounds nuw i8, ptr %145, i64 264
  %407 = load volatile i64, ptr %406, align 8, !tbaa !30
  %408 = getelementptr inbounds nuw i8, ptr %145, i64 272
  %409 = load volatile i64, ptr %408, align 8, !tbaa !32
  %410 = call fastcc zeroext i32 @map_field_idx(i64 noundef %407, i64 noundef %409) #8
  %411 = shl nuw nsw i32 %410, 5
  %412 = zext nneg i32 %411 to i64
  %413 = getelementptr inbounds nuw i8, ptr @labels_page_21, i64 %412
  br label %433

414:                                              ; preds = %159
  %415 = getelementptr inbounds nuw i8, ptr %145, i64 744
  %416 = load volatile i64, ptr %415, align 8, !tbaa !30
  %417 = getelementptr inbounds nuw i8, ptr %145, i64 752
  %418 = load volatile i64, ptr %417, align 8, !tbaa !32
  %419 = call fastcc zeroext i32 @map_field_idx(i64 noundef %416, i64 noundef %418) #8
  %420 = shl nuw nsw i32 %419, 5
  %421 = zext nneg i32 %420 to i64
  %422 = getelementptr inbounds nuw i8, ptr @labels_page_22, i64 %421
  br label %433

423:                                              ; preds = %159
  %424 = getelementptr inbounds nuw i8, ptr %145, i64 1008
  %425 = load volatile i64, ptr %424, align 8, !tbaa !30
  %426 = getelementptr inbounds nuw i8, ptr %145, i64 1016
  %427 = load volatile i64, ptr %426, align 8, !tbaa !32
  %428 = call fastcc zeroext i32 @map_field_idx(i64 noundef %425, i64 noundef %427) #8
  %429 = shl nuw nsw i32 %428, 5
  %430 = zext nneg i32 %429 to i64
  %431 = getelementptr inbounds nuw i8, ptr @labels_page_23, i64 %430
  br label %433

432:                                              ; preds = %159
  unreachable

433:                                              ; preds = %144, %423, %414, %405, %396, %387, %378, %369, %360, %351, %342, %333, %324, %315, %306, %297, %288, %279, %270, %261, %252, %243, %234, %226, %216, %136, %140
  %434 = phi ptr [ inttoptr (i64 3165888 to ptr), %136 ], [ inttoptr (i64 3165888 to ptr), %140 ], [ inttoptr (i64 3165888 to ptr), %144 ], [ %431, %423 ], [ %225, %216 ], [ %233, %226 ], [ %242, %234 ], [ %251, %243 ], [ %260, %252 ], [ %269, %261 ], [ %278, %270 ], [ %287, %279 ], [ %296, %288 ], [ %305, %297 ], [ %314, %306 ], [ %323, %315 ], [ %332, %324 ], [ %341, %333 ], [ %350, %342 ], [ %359, %351 ], [ %368, %360 ], [ %377, %369 ], [ %386, %378 ], [ %395, %387 ], [ %404, %396 ], [ %413, %405 ], [ %422, %414 ]
  ret ptr %434
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc ptr @get_arena() unnamed_addr #2 {
  %1 = load volatile i64, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !18
  %2 = tail call fastcc signext i32 @arena_rw(i64 noundef %1) #8
  %3 = icmp eq i32 %2, 0
  %4 = inttoptr i64 %1 to ptr
  %5 = select i1 %3, ptr null, ptr %4
  ret ptr %5
}

; Function Attrs: minsize optsize
declare i64 @native_clock() local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize mustprogress nofree norecurse nosync nounwind optsize willreturn memory(none)
define internal fastcc zeroext range(i32 0, 263) i32 @map_field_idx(i64 noundef %0, i64 noundef %1) unnamed_addr #4 {
  switch i64 %0, label %8 [
    i64 0, label %9
    i64 -6, label %13
    i64 -4, label %3
    i64 -3, label %4
    i64 -5, label %5
    i64 -1, label %6
    i64 -2, label %7
  ]

3:                                                ; preds = %2
  br label %13

4:                                                ; preds = %2
  br label %13

5:                                                ; preds = %2
  br label %13

6:                                                ; preds = %2
  br label %13

7:                                                ; preds = %2
  br label %13

8:                                                ; preds = %2
  br label %13

9:                                                ; preds = %2
  %10 = trunc i64 %1 to i32
  %11 = and i32 %10, 255
  %12 = add nuw nsw i32 %11, 7
  br label %13

13:                                               ; preds = %2, %9, %8, %7, %6, %5, %4, %3
  %14 = phi i32 [ %12, %9 ], [ 1, %3 ], [ 2, %4 ], [ 3, %5 ], [ 4, %6 ], [ 5, %7 ], [ 6, %8 ], [ 0, %2 ]
  ret i32 %14
}

; Function Attrs: minsize mustprogress nofree norecurse nosync nounwind optsize willreturn memory(none)
define internal fastcc zeroext range(i32 0, 268) i32 @map_blk_idx(i64 noundef %0, i64 noundef %1) unnamed_addr #4 {
  switch i64 %0, label %6 [
    i64 0, label %7
    i64 -6, label %19
    i64 -4, label %3
    i64 -3, label %4
    i64 -5, label %5
  ]

3:                                                ; preds = %2
  br label %19

4:                                                ; preds = %2
  br label %19

5:                                                ; preds = %2
  br label %19

6:                                                ; preds = %2
  br label %19

7:                                                ; preds = %2
  switch i64 %1, label %14 [
    i64 0, label %19
    i64 512, label %8
    i64 1024, label %9
    i64 2048, label %10
    i64 4096, label %11
    i64 2352, label %12
    i64 2064, label %13
  ]

8:                                                ; preds = %7
  br label %19

9:                                                ; preds = %7
  br label %19

10:                                               ; preds = %7
  br label %19

11:                                               ; preds = %7
  br label %19

12:                                               ; preds = %7
  br label %19

13:                                               ; preds = %7
  br label %19

14:                                               ; preds = %7
  %15 = trunc i64 %1 to i32
  %16 = lshr i32 %15, 8
  %17 = and i32 %16, 255
  %18 = add nuw nsw i32 %17, 12
  br label %19

19:                                               ; preds = %7, %2, %14, %13, %12, %11, %10, %9, %8, %6, %5, %4, %3
  %20 = phi i32 [ %18, %14 ], [ 1, %3 ], [ 2, %4 ], [ 3, %5 ], [ 4, %6 ], [ 0, %2 ], [ 6, %8 ], [ 7, %9 ], [ 8, %10 ], [ 9, %11 ], [ 10, %12 ], [ 11, %13 ], [ 5, %7 ]
  ret i32 %20
}

; Function Attrs: minsize optsize
declare i64 @native_alloc(i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #3

; Function Attrs: minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite)
define internal fastcc signext range(i32 0, 2) i32 @arena_rw(i64 noundef %0) unnamed_addr #2 {
  %2 = load volatile i64, ptr inttoptr (i64 9652608 to ptr), align 128, !tbaa !9
  %3 = and i64 %2, -260046849
  %4 = icmp eq i64 %3, 2147483648
  br i1 %4, label %5, label %22

5:                                                ; preds = %1
  %6 = load volatile i64, ptr inttoptr (i64 38102456 to ptr), align 8, !tbaa !9
  %7 = icmp eq i64 %6, %2
  br i1 %7, label %8, label %22

8:                                                ; preds = %5
  %9 = load volatile i64, ptr inttoptr (i64 38036872 to ptr), align 8, !tbaa !9
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

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
define internal fastcc void @dump_node(ptr nofree noundef captures(address) %0, i32 noundef zeroext range(i32 0, 256) %1, i32 noundef zeroext range(i32 0, 256) %2) unnamed_addr #0 {
  %4 = zext nneg i32 %1 to i64
  %5 = or disjoint i64 %4, 7094703231829278720
  %6 = zext nneg i32 %2 to i64
  %7 = or disjoint i64 %6, 7234318118812647424
  tail call fastcc void @read_one_field(ptr noundef %0, i64 noundef %5, i64 noundef %7, i64 noundef 8392862959675637760, i64 noundef 0) #8
  %8 = getelementptr inbounds nuw i8, ptr %0, i64 24
  tail call fastcc void @read_one_field(ptr noundef nonnull %8, i64 noundef %5, i64 noundef %7, i64 noundef 7594194871653498880, i64 noundef 0) #8
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 48
  tail call fastcc void @read_one_field(ptr noundef nonnull %9, i64 noundef %5, i64 noundef %7, i64 noundef 8101820097204584448, i64 noundef 0) #8
  %10 = getelementptr inbounds nuw i8, ptr %0, i64 72
  tail call fastcc void @read_one_field(ptr noundef nonnull %10, i64 noundef %5, i64 noundef %7, i64 noundef 7092161570904046181, i64 noundef 0) #8
  %11 = getelementptr inbounds nuw i8, ptr %0, i64 96
  tail call fastcc void @read_one_field(ptr noundef nonnull %11, i64 noundef %5, i64 noundef %7, i64 noundef 7953183684824361843, i64 noundef 0) #8
  %12 = getelementptr inbounds nuw i8, ptr %0, i64 120
  tail call fastcc void @read_one_field(ptr noundef nonnull %12, i64 noundef %5, i64 noundef %7, i64 noundef 7953201246812438528, i64 noundef 0) #8
  %13 = getelementptr inbounds nuw i8, ptr %0, i64 144
  tail call fastcc void @read_one_field(ptr noundef nonnull %13, i64 noundef %5, i64 noundef %7, i64 noundef 7882817105260277351, i64 noundef 0) #8
  %14 = getelementptr inbounds nuw i8, ptr %0, i64 168
  tail call fastcc void @read_one_field(ptr noundef nonnull %14, i64 noundef %5, i64 noundef %7, i64 noundef 8098432413336957696, i64 noundef 0) #8
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 192
  tail call fastcc void @read_one_field(ptr noundef nonnull %15, i64 noundef %5, i64 noundef %7, i64 noundef 8098432413369464320, i64 noundef 0) #8
  %16 = getelementptr inbounds nuw i8, ptr %0, i64 216
  tail call fastcc void @read_one_field(ptr noundef nonnull %16, i64 noundef %5, i64 noundef %7, i64 noundef 8098432413404065280, i64 noundef 0) #8
  %17 = getelementptr inbounds nuw i8, ptr %0, i64 240
  tail call fastcc void @read_one_field(ptr noundef nonnull %17, i64 noundef %5, i64 noundef %7, i64 noundef 7597137654395699200, i64 noundef 0) #8
  %18 = getelementptr inbounds nuw i8, ptr %0, i64 264
  tail call fastcc void @read_one_field(ptr noundef nonnull %18, i64 noundef %5, i64 noundef %7, i64 noundef 7597137654395699201, i64 noundef 0) #8
  %19 = getelementptr inbounds nuw i8, ptr %0, i64 288
  tail call fastcc void @read_one_field(ptr noundef nonnull %19, i64 noundef %5, i64 noundef %7, i64 noundef 7597137654395699202, i64 noundef 0) #8
  %20 = getelementptr inbounds nuw i8, ptr %0, i64 312
  tail call fastcc void @read_one_field(ptr noundef nonnull %20, i64 noundef %5, i64 noundef %7, i64 noundef 7597137654395699203, i64 noundef 0) #8
  %21 = getelementptr inbounds nuw i8, ptr %0, i64 336
  tail call fastcc void @read_one_field(ptr noundef nonnull %21, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221888, i64 noundef 8392862959675637760) #8
  %22 = getelementptr inbounds nuw i8, ptr %0, i64 360
  tail call fastcc void @read_one_field(ptr noundef nonnull %22, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221888, i64 noundef 7233190436494376960) #8
  %23 = getelementptr inbounds nuw i8, ptr %0, i64 384
  tail call fastcc void @read_one_field(ptr noundef nonnull %23, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221889, i64 noundef 8392862959675637760) #8
  %24 = getelementptr inbounds nuw i8, ptr %0, i64 408
  tail call fastcc void @read_one_field(ptr noundef nonnull %24, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221889, i64 noundef 7233190436494376960) #8
  %25 = getelementptr inbounds nuw i8, ptr %0, i64 432
  tail call fastcc void @read_one_field(ptr noundef nonnull %25, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221890, i64 noundef 8392862959675637760) #8
  %26 = getelementptr inbounds nuw i8, ptr %0, i64 456
  tail call fastcc void @read_one_field(ptr noundef nonnull %26, i64 noundef %5, i64 noundef %7, i64 noundef 8243107942669221890, i64 noundef 7233190436494376960) #8
  ret void
}

; Function Attrs: minsize nounwind optsize
define internal fastcc void @read_one_field(ptr nofree noundef captures(address) %0, i64 noundef range(i64 7094703231829278720, 7094703231829278976) %1, i64 noundef range(i64 7234318118812647424, 8392862959675637761) %2, i64 noundef range(i64 0, 8392862959675637761) %3, i64 noundef range(i64 0, 8392862959675637761) %4) unnamed_addr #0 {
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #6
  store i64 0, ptr %6, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #6
  store i64 0, ptr %7, align 8, !tbaa !9
  %8 = call i64 @repo_read(ptr noundef nonnull %6, ptr noundef nonnull %7, i64 noundef %1, i64 noundef %2, i64 noundef %3, i64 noundef %4) #7
  %9 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %10 = add i32 %9, 1
  store volatile i32 %10, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !22
  %11 = icmp eq i64 %8, 0
  br i1 %11, label %17, label %12

12:                                               ; preds = %5
  %13 = load volatile i32, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !23
  %14 = icmp eq i32 %13, 0
  br i1 %14, label %15, label %17

15:                                               ; preds = %12
  %16 = trunc i64 %8 to i32
  store volatile i32 %16, ptr inttoptr (i64 9637680 to ptr), align 16, !tbaa !23
  br label %17

17:                                               ; preds = %15, %12, %5
  store volatile i64 %8, ptr %0, align 8, !tbaa !30
  %18 = load i64, ptr %6, align 8, !tbaa !9
  %19 = getelementptr inbounds nuw i8, ptr %0, i64 8
  store volatile i64 %18, ptr %19, align 8, !tbaa !32
  %20 = load i64, ptr %7, align 8, !tbaa !9
  %21 = getelementptr inbounds nuw i8, ptr %0, i64 16
  store volatile i64 %20, ptr %21, align 8, !tbaa !33
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #6
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #6
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.umin.i64(i64, i64) #5

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.umin.i32(i32, i32) #5

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize nofree noinline norecurse nosync nounwind optsize memory(readwrite) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #3 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #4 = { minsize mustprogress nofree norecurse nosync nounwind optsize willreturn memory(none) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #5 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nounwind }
attributes #7 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #8 = { minsize nobuiltin optsize "no-builtins" }

!llvm.ident = !{!0}
!llvm.errno.tbaa = !{!1}

!0 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!1 = !{!2, !3, i64 0}
!2 = !{!"__libc_errno", !3, i64 0}
!3 = !{!"int", !4, i64 0}
!4 = !{!"omnipotent char", !5, i64 0}
!5 = !{!"Simple C/C++ TBAA"}
!6 = !{!7, !3, i64 0}
!7 = !{!"ProbeState", !3, i64 0, !3, i64 4, !3, i64 8, !3, i64 12, !3, i64 16, !3, i64 20, !4, i64 24, !8, i64 32, !4, i64 40, !4, i64 41, !4, i64 42, !4, i64 43, !4, i64 44, !4, i64 45, !4, i64 46, !8, i64 48, !8, i64 56, !8, i64 64, !8, i64 72, !8, i64 80, !8, i64 88}
!8 = !{!"long long", !4, i64 0}
!9 = !{!8, !8, i64 0}
!10 = !{!7, !4, i64 40}
!11 = !{!7, !4, i64 41}
!12 = !{!7, !4, i64 42}
!13 = !{!7, !4, i64 43}
!14 = !{!7, !4, i64 44}
!15 = !{!7, !4, i64 45}
!16 = !{!7, !3, i64 20}
!17 = !{!7, !8, i64 80}
!18 = !{!7, !8, i64 32}
!19 = !{!4, !4, i64 0}
!20 = distinct !{!20, !21}
!21 = !{!"llvm.loop.mustprogress"}
!22 = !{!7, !3, i64 4}
!23 = !{!7, !3, i64 16}
!24 = !{!7, !3, i64 8}
!25 = !{!7, !3, i64 12}
!26 = distinct !{!26, !21}
!27 = distinct !{!27, !21}
!28 = !{!7, !8, i64 48}
!29 = !{!7, !8, i64 56}
!30 = !{!31, !8, i64 0}
!31 = !{!"FieldRecord", !8, i64 0, !8, i64 8, !8, i64 16}
!32 = !{!31, !8, i64 8}
!33 = !{!31, !8, i64 16}
