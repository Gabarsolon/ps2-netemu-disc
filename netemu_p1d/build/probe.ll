; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@labels_page_a = external constant [0 x i8], align 1
@labels_page_b = external constant [0 x i8], align 1
@labels_page_c = external constant [0 x i8], align 1
@labels_page_d = external constant [0 x i8], align 1
@switch.table.s4_menu = private unnamed_addr constant [7 x i8] c"\02\06\05\04\03\01\00", align 4
@switch.table.map_rc_idx = private unnamed_addr constant [18 x i8] c"\0A\0B\0B\0B\0B\0B\09\08\07\0B\0B\06\05\04\03\02\0B\01", align 4

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %5 = and i32 %4, 1
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %97

7:                                                ; preds = %1
  %8 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %9 = or i32 %8, 1
  store volatile i32 %9, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #4
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #4
  store volatile i8 -1, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !9
  store volatile i8 -1, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !10
  store volatile i8 -1, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !11
  store volatile i8 -1, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !12
  store volatile i8 -1, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !13
  store volatile i8 -1, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !14
  store volatile i8 -1, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !15
  br label %10

10:                                               ; preds = %92, %7
  %11 = phi i64 [ %93, %92 ], [ 0, %7 ]
  %12 = icmp eq i64 %11, 16
  br i1 %12, label %94, label %13

13:                                               ; preds = %10
  %14 = or disjoint i64 %11, 7094703231829278720
  store i64 0, ptr %2, align 8, !tbaa !16
  store i64 0, ptr %3, align 8, !tbaa !16
  %15 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %14, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #5
  %16 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %17 = add i32 %16, 1
  store volatile i32 %17, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %18 = icmp eq i64 %15, 0
  br i1 %18, label %24, label %19

19:                                               ; preds = %13
  %20 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !18
  %21 = icmp eq i32 %20, 0
  br i1 %21, label %22, label %92

22:                                               ; preds = %19
  %23 = trunc i64 %15 to i32
  store volatile i32 %23, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !18
  br label %92

24:                                               ; preds = %13
  %25 = load i64, ptr %2, align 8, !tbaa !16
  %26 = icmp eq i64 %25, 5
  %27 = trunc i64 %11 to i8
  br i1 %26, label %28, label %29

28:                                               ; preds = %24
  store volatile i8 %27, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !9
  br label %29

29:                                               ; preds = %28, %24
  store i64 0, ptr %2, align 8, !tbaa !16
  store i64 0, ptr %3, align 8, !tbaa !16
  %30 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %14, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #5
  %31 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %32 = add i32 %31, 1
  store volatile i32 %32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %33 = icmp eq i64 %30, 0
  %34 = load i64, ptr %2, align 8
  %35 = select i1 %33, i64 %34, i64 0
  %36 = icmp eq i64 %11, 4
  br label %37

37:                                               ; preds = %90, %29
  %38 = phi i64 [ %91, %90 ], [ 0, %29 ]
  %39 = icmp eq i64 %38, 16
  br i1 %39, label %92, label %40

40:                                               ; preds = %37
  %41 = or disjoint i64 %38, 7234318118812647424
  store i64 0, ptr %2, align 8, !tbaa !16
  store i64 0, ptr %3, align 8, !tbaa !16
  %42 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %14, i64 noundef %41, i64 noundef 8392862959675637760, i64 noundef 0) #5
  %43 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %44 = add i32 %43, 1
  store volatile i32 %44, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %45 = icmp eq i64 %42, 0
  br i1 %45, label %46, label %90

46:                                               ; preds = %40
  %47 = load i64, ptr %2, align 8, !tbaa !16
  %48 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !19
  %49 = add i32 %48, 1
  store volatile i32 %49, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !19
  store i64 0, ptr %2, align 8, !tbaa !16
  store i64 0, ptr %3, align 8, !tbaa !16
  %50 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %14, i64 noundef %41, i64 noundef 7594194871653498880, i64 noundef 0) #5
  %51 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %52 = add i32 %51, 1
  store volatile i32 %52, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %53 = icmp eq i64 %50, 0
  %54 = load i64, ptr %2, align 8
  %55 = select i1 %53, i64 %54, i64 0
  store i64 0, ptr %2, align 8, !tbaa !16
  store i64 0, ptr %3, align 8, !tbaa !16
  %56 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %14, i64 noundef %41, i64 noundef 8101820097204584448, i64 noundef 0) #5
  %57 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %58 = add i32 %57, 1
  store volatile i32 %58, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %59 = icmp eq i64 %56, 0
  %60 = load i64, ptr %2, align 8
  %61 = trunc i64 %60 to i32
  %62 = select i1 %59, i32 %61, i32 255
  %63 = icmp eq i64 %47, 5
  br i1 %63, label %64, label %80

64:                                               ; preds = %46
  %65 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %66 = add i32 %65, 1
  store volatile i32 %66, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %67 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %68 = icmp eq i32 %67, 1
  br i1 %68, label %69, label %72

69:                                               ; preds = %64
  store volatile i8 %27, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !10
  %70 = trunc i64 %38 to i8
  store volatile i8 %70, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !11
  %71 = trunc i32 %62 to i8
  store volatile i8 %71, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !12
  store volatile i64 %35, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  store volatile i64 %55, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  br label %72

72:                                               ; preds = %69, %64
  br i1 %26, label %73, label %76

73:                                               ; preds = %72
  %74 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !23
  %75 = or i8 %74, 1
  store volatile i8 %75, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !23
  br label %76

76:                                               ; preds = %73, %72
  br i1 %36, label %77, label %90

77:                                               ; preds = %76
  %78 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !23
  %79 = or i8 %78, 2
  store volatile i8 %79, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !23
  br label %90

80:                                               ; preds = %46
  %81 = icmp eq i64 %47, 0
  %82 = select i1 %36, i1 %81, i1 false
  %83 = icmp eq i32 %62, 2
  %84 = select i1 %82, i1 %83, i1 false
  br i1 %84, label %85, label %90

85:                                               ; preds = %80
  %86 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !24
  %87 = icmp eq i32 %86, 0
  br i1 %87, label %88, label %90

88:                                               ; preds = %85
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !24
  store volatile i8 4, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !13
  %89 = trunc i64 %38 to i8
  store volatile i8 %89, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !14
  store volatile i8 2, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !15
  store volatile i64 %35, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !25
  store volatile i64 %55, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !26
  br label %90

90:                                               ; preds = %88, %85, %80, %77, %76, %40
  %91 = add nuw nsw i64 %38, 1
  br label %37, !llvm.loop !27

92:                                               ; preds = %37, %22, %19
  %93 = add nuw nsw i64 %11, 1
  br label %10, !llvm.loop !29

94:                                               ; preds = %10
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #4
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #4
  %95 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %96 = or i32 %95, 2
  store volatile i32 %96, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %97

97:                                               ; preds = %94, %1
  %98 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %99 = and i32 %98, 2
  %100 = icmp eq i32 %99, 0
  br i1 %100, label %256, label %101

101:                                              ; preds = %97
  %102 = trunc i64 %0 to i32
  %103 = and i32 %102, 3
  switch i32 %103, label %255 [
    i32 0, label %104
    i32 1, label %115
    i32 2, label %189
    i32 3, label %227
  ]

104:                                              ; preds = %101
  %105 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %106 = icmp ugt i32 %105, 4
  br i1 %106, label %112, label %107

107:                                              ; preds = %104
  %108 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %109 = mul i32 %108, 720
  %110 = add i32 %109, 576
  %111 = zext i32 %110 to i64
  br label %112

112:                                              ; preds = %104, %107
  %113 = phi i64 [ %111, %107 ], [ 3456, %104 ]
  %114 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %113
  br label %256

115:                                              ; preds = %101
  %116 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !20
  %117 = icmp eq i32 %116, 0
  br i1 %117, label %256, label %118

118:                                              ; preds = %115
  %119 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !10
  %120 = icmp ugt i8 %119, 15
  br i1 %120, label %124, label %121

121:                                              ; preds = %118
  %122 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !10
  %123 = zext i8 %122 to i32
  br label %124

124:                                              ; preds = %118, %121
  %125 = phi i32 [ %123, %121 ], [ 15, %118 ]
  %126 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !11
  %127 = icmp ugt i8 %126, 15
  br i1 %127, label %131, label %128

128:                                              ; preds = %124
  %129 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !11
  %130 = zext i8 %129 to i32
  br label %131

131:                                              ; preds = %124, %128
  %132 = phi i32 [ %130, %128 ], [ 15, %124 ]
  %133 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !12
  %134 = icmp ult i8 %133, 3
  br i1 %134, label %135, label %138

135:                                              ; preds = %131
  %136 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !12
  %137 = zext i8 %136 to i32
  br label %138

138:                                              ; preds = %131, %135
  %139 = phi i32 [ %137, %135 ], [ 3, %131 ]
  %140 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %141 = zext nneg i32 %125 to i64
  %142 = icmp eq i64 %140, %141
  br i1 %142, label %143, label %147

143:                                              ; preds = %138
  %144 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %145 = zext nneg i32 %132 to i64
  %146 = icmp eq i64 %144, %145
  br i1 %146, label %178, label %147

147:                                              ; preds = %143, %138
  %148 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %149 = icmp eq i64 %148, 1280
  br i1 %149, label %150, label %153

150:                                              ; preds = %147
  %151 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %152 = icmp eq i64 %151, 1281
  br i1 %152, label %178, label %153

153:                                              ; preds = %150, %147
  %154 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %155 = icmp eq i64 %154, 256
  br i1 %155, label %156, label %159

156:                                              ; preds = %153
  %157 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %158 = icmp eq i64 %157, 512
  br i1 %158, label %178, label %159

159:                                              ; preds = %156, %153
  %160 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %161 = icmp eq i64 %160, 4
  br i1 %161, label %162, label %165

162:                                              ; preds = %159
  %163 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %164 = icmp eq i64 %163, 0
  br i1 %164, label %178, label %165

165:                                              ; preds = %162, %159
  %166 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %167 = icmp eq i64 %166, 5
  br i1 %167, label %168, label %171

168:                                              ; preds = %165
  %169 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %170 = icmp eq i64 %169, 2
  br i1 %170, label %178, label %171

171:                                              ; preds = %168, %165
  %172 = load volatile i64, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !21
  %173 = icmp eq i64 %172, 0
  br i1 %173, label %174, label %178

174:                                              ; preds = %171
  %175 = load volatile i64, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !22
  %176 = icmp eq i64 %175, 0
  %177 = select i1 %176, i32 80, i32 96
  br label %178

178:                                              ; preds = %174, %168, %162, %156, %150, %143, %171
  %179 = phi i32 [ 96, %171 ], [ 0, %143 ], [ 16, %150 ], [ 32, %156 ], [ 48, %162 ], [ 64, %168 ], [ %177, %174 ]
  %180 = add nuw nsw i32 %179, %125
  %181 = shl nuw nsw i32 %180, 6
  %182 = shl nuw nsw i32 %132, 2
  %183 = or disjoint i32 %182, 1
  %184 = add nuw nsw i32 %183, %139
  %185 = add nuw nsw i32 %184, %181
  %186 = mul nuw nsw i32 %185, 48
  %187 = zext nneg i32 %186 to i64
  %188 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %187
  br label %256

189:                                              ; preds = %101
  %190 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !24
  %191 = icmp eq i32 %190, 0
  br i1 %191, label %256, label %192

192:                                              ; preds = %189
  %193 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !13
  %194 = icmp ult i8 %193, 8
  br i1 %194, label %195, label %199

195:                                              ; preds = %192
  %196 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !13
  %197 = zext i8 %196 to i64
  %198 = mul nuw nsw i64 %197, 5
  br label %199

199:                                              ; preds = %192, %195
  %200 = phi i64 [ %198, %195 ], [ 40, %192 ]
  %201 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !14
  %202 = icmp ult i8 %201, 4
  br i1 %202, label %203, label %206

203:                                              ; preds = %199
  %204 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !14
  %205 = zext i8 %204 to i64
  br label %206

206:                                              ; preds = %199, %203
  %207 = phi i64 [ %205, %203 ], [ 4, %199 ]
  %208 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !15
  %209 = icmp ult i8 %208, 4
  br i1 %209, label %210, label %213

210:                                              ; preds = %206
  %211 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !15
  %212 = zext i8 %211 to i64
  br label %213

213:                                              ; preds = %206, %210
  %214 = phi i64 [ %212, %210 ], [ 4, %206 ]
  %215 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !23
  %216 = and i8 %215, 3
  %217 = zext nneg i8 %216 to i64
  %218 = add nuw nsw i64 %207, %200
  %219 = mul nuw nsw i64 %218, 5
  %220 = add nuw nsw i64 %214, %219
  %221 = shl nuw nsw i64 %220, 2
  %222 = or disjoint i64 %221, 1
  %223 = add nuw nsw i64 %222, %217
  %224 = mul nuw nsw i64 %223, 48
  %225 = and i64 %224, 4294967280
  %226 = getelementptr inbounds nuw i8, ptr @labels_page_c, i64 %225
  br label %256

227:                                              ; preds = %101
  %228 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %229 = lshr i32 %228, 2
  %230 = and i32 %229, 1
  %231 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %232 = lshr i32 %231, 4
  %233 = and i32 %232, 1
  %234 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !30
  %235 = call fastcc zeroext i32 @map_rc_idx(i64 noundef %234, i32 noundef zeroext %230) #6
  %236 = load volatile i64, ptr inttoptr (i64 9637752 to ptr), align 8, !tbaa !31
  %237 = call fastcc zeroext i32 @map_rc_idx(i64 noundef %236, i32 noundef zeroext %233) #6
  %238 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !18
  %239 = add i32 %238, 6
  %240 = icmp ult i32 %239, 7
  br i1 %240, label %241, label %246

241:                                              ; preds = %227
  %242 = zext nneg i32 %239 to i64
  %243 = getelementptr inbounds nuw i8, ptr @switch.table.s4_menu, i64 %242
  %244 = load i8, ptr %243, align 1
  %245 = zext i8 %244 to i32
  br label %246

246:                                              ; preds = %227, %241
  %247 = phi i32 [ %245, %241 ], [ 7, %227 ]
  %248 = mul nuw nsw i32 %235, 12
  %249 = add nuw nsw i32 %237, %248
  %250 = shl nuw nsw i32 %249, 3
  %251 = or disjoint i32 %247, %250
  %252 = mul nuw nsw i32 %251, 48
  %253 = zext nneg i32 %252 to i64
  %254 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %253
  br label %256

255:                                              ; preds = %101
  unreachable

256:                                              ; preds = %112, %178, %213, %246, %115, %189, %97
  %257 = phi ptr [ inttoptr (i64 3165888 to ptr), %97 ], [ %254, %246 ], [ %114, %112 ], [ @labels_page_b, %115 ], [ %188, %178 ], [ %226, %213 ], [ @labels_page_c, %189 ]
  ret ptr %257
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize mustprogress nofree norecurse nosync nounwind optsize willreturn memory(none)
define internal fastcc zeroext range(i32 0, 12) i32 @map_rc_idx(i64 noundef %0, i32 noundef zeroext range(i32 0, 2) %1) unnamed_addr #2 {
  %3 = icmp eq i32 %1, 0
  br i1 %3, label %11, label %4

4:                                                ; preds = %2
  %5 = add i64 %0, 17
  %6 = icmp ult i64 %5, 18
  br i1 %6, label %7, label %11

7:                                                ; preds = %4
  %8 = getelementptr inbounds nuw i8, ptr @switch.table.map_rc_idx, i64 %5
  %9 = load i8, ptr %8, align 1
  %10 = zext i8 %9 to i32
  br label %11

11:                                               ; preds = %4, %7, %2
  %12 = phi i32 [ 0, %2 ], [ %10, %7 ], [ 11, %4 ]
  ret i32 %12
}

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #3

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize mustprogress nofree norecurse nosync nounwind optsize willreturn memory(none) "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #3 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #4 = { nounwind }
attributes #5 = { minsize nobuiltin nounwind optsize "no-builtins" }
attributes #6 = { minsize nobuiltin optsize "no-builtins" }

!llvm.ident = !{!0}
!llvm.errno.tbaa = !{!1}

!0 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!1 = !{!2, !3, i64 0}
!2 = !{!"__libc_errno", !3, i64 0}
!3 = !{!"int", !4, i64 0}
!4 = !{!"omnipotent char", !5, i64 0}
!5 = !{!"Simple C/C++ TBAA"}
!6 = !{!7, !3, i64 0}
!7 = !{!"ProbeState", !3, i64 0, !3, i64 4, !3, i64 8, !3, i64 12, !3, i64 16, !3, i64 20, !3, i64 24, !3, i64 28, !4, i64 32, !4, i64 33, !4, i64 34, !4, i64 35, !4, i64 36, !4, i64 37, !4, i64 38, !4, i64 39, !3, i64 40, !3, i64 44, !8, i64 48, !8, i64 56, !8, i64 64, !8, i64 72, !8, i64 80, !8, i64 88}
!8 = !{!"long long", !4, i64 0}
!9 = !{!7, !4, i64 35}
!10 = !{!7, !4, i64 32}
!11 = !{!7, !4, i64 33}
!12 = !{!7, !4, i64 34}
!13 = !{!7, !4, i64 36}
!14 = !{!7, !4, i64 37}
!15 = !{!7, !4, i64 38}
!16 = !{!8, !8, i64 0}
!17 = !{!7, !3, i64 20}
!18 = !{!7, !3, i64 24}
!19 = !{!7, !3, i64 4}
!20 = !{!7, !3, i64 8}
!21 = !{!7, !8, i64 64}
!22 = !{!7, !8, i64 72}
!23 = !{!7, !4, i64 39}
!24 = !{!7, !3, i64 12}
!25 = !{!7, !8, i64 48}
!26 = !{!7, !8, i64 56}
!27 = distinct !{!27, !28}
!28 = !{!"llvm.loop.mustprogress"}
!29 = distinct !{!29, !28}
!30 = !{!7, !8, i64 80}
!31 = !{!7, !8, i64 88}
