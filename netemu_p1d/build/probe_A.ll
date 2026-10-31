; ModuleID = 'src/probe.c'
source_filename = "src/probe.c"
target datalayout = "E-m:e-Fn32-i64:64-i128:128-n32:64-S128-v256:256:256-v512:512:512"
target triple = "powerpc64-unknown-linux-gnu"

@labels_page_a = external constant [0 x i8], align 1
@labels_page_b = external constant [0 x i8], align 1
@labels_page_c = external constant [0 x i8], align 1
@labels_page_d = external constant [0 x i8], align 1
@switch.table.s4_menu = private unnamed_addr constant [18 x i16] [i16 640, i16 704, i16 704, i16 704, i16 704, i16 704, i16 576, i16 512, i16 448, i16 704, i16 704, i16 384, i16 320, i16 256, i16 192, i16 128, i16 704, i16 64], align 8
@switch.table.s4_menu.1 = private unnamed_addr constant [18 x i32] [i32 61440, i32 67584, i32 67584, i32 67584, i32 67584, i32 67584, i32 55296, i32 49152, i32 43008, i32 67584, i32 67584, i32 36864, i32 30720, i32 24576, i32 18432, i32 12288, i32 67584, i32 6144], align 8
@switch.table.s4_menu.2 = private unnamed_addr constant [18 x i16] [i16 5120, i16 5632, i16 5632, i16 5632, i16 5632, i16 5632, i16 4608, i16 4096, i16 3584, i16 5632, i16 5632, i16 3072, i16 2560, i16 2048, i16 1536, i16 1024, i16 5632, i16 512], align 8
@switch.table.s4_menu.3 = private unnamed_addr constant [7 x i16] [i16 128, i16 384, i16 320, i16 256, i16 192, i16 64, i16 0], align 8

; Function Attrs: minsize nounwind optsize
define dso_local nonnull ptr @s4_menu(i64 noundef %0) local_unnamed_addr #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %5 = and i32 %4, 1
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %108

7:                                                ; preds = %1
  %8 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %9 = or i32 %8, 1
  store volatile i32 %9, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #3
  store i64 0, ptr %2, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #3
  store i64 0, ptr %3, align 8, !tbaa !9
  store volatile i8 -1, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !10
  store volatile i8 -1, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  store volatile i8 -1, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  store volatile i8 -1, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  store volatile i8 -1, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  store volatile i8 -1, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  store volatile i8 -1, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  br label %10

10:                                               ; preds = %100, %7
  %11 = phi i64 [ %101, %100 ], [ 0, %7 ]
  %12 = icmp eq i64 %11, 16
  br i1 %12, label %13, label %21

13:                                               ; preds = %10
  %14 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %15 = or i32 %14, 4
  store volatile i32 %15, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %16 = call i64 @lv1_open_device(i64 noundef 9, i64 noundef 0, i64 noundef 0) #4
  %17 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %18 = add i32 %17, 1
  store volatile i32 %18, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  store volatile i64 %16, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !18
  %19 = trunc i64 %16 to i32
  store volatile i32 %19, ptr inttoptr (i64 9637704 to ptr), align 8, !tbaa !19
  %20 = icmp eq i64 %16, 0
  br i1 %20, label %102, label %105

21:                                               ; preds = %10
  %22 = or disjoint i64 %11, 7094703231829278720
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %23 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 8392862959675637760, i64 noundef 0, i64 noundef 0) #4
  %24 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %25 = add i32 %24, 1
  store volatile i32 %25, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %26 = icmp eq i64 %23, 0
  br i1 %26, label %32, label %27

27:                                               ; preds = %21
  %28 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %29 = icmp eq i32 %28, 0
  br i1 %29, label %30, label %100

30:                                               ; preds = %27
  %31 = trunc i64 %23 to i32
  store volatile i32 %31, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  br label %100

32:                                               ; preds = %21
  %33 = load i64, ptr %2, align 8, !tbaa !9
  %34 = icmp eq i64 %33, 5
  %35 = trunc i64 %11 to i8
  br i1 %34, label %36, label %37

36:                                               ; preds = %32
  store volatile i8 %35, ptr inttoptr (i64 9637699 to ptr), align 1, !tbaa !10
  br label %37

37:                                               ; preds = %36, %32
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %38 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef 7594194871653498880, i64 noundef 0, i64 noundef 0) #4
  %39 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %40 = add i32 %39, 1
  store volatile i32 %40, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %41 = icmp eq i64 %38, 0
  %42 = load i64, ptr %2, align 8
  %43 = select i1 %41, i64 %42, i64 0
  %44 = icmp eq i64 %11, 4
  br label %45

45:                                               ; preds = %98, %37
  %46 = phi i64 [ %99, %98 ], [ 0, %37 ]
  %47 = icmp eq i64 %46, 16
  br i1 %47, label %100, label %48

48:                                               ; preds = %45
  %49 = or disjoint i64 %46, 7234318118812647424
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %50 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8392862959675637760, i64 noundef 0) #4
  %51 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %52 = add i32 %51, 1
  store volatile i32 %52, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %53 = icmp eq i64 %50, 0
  br i1 %53, label %54, label %98

54:                                               ; preds = %48
  %55 = load i64, ptr %2, align 8, !tbaa !9
  %56 = load volatile i32, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !21
  %57 = add i32 %56, 1
  store volatile i32 %57, ptr inttoptr (i64 9637668 to ptr), align 4, !tbaa !21
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %58 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 7594194871653498880, i64 noundef 0) #4
  %59 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %60 = add i32 %59, 1
  store volatile i32 %60, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %61 = icmp eq i64 %58, 0
  %62 = load i64, ptr %2, align 8
  %63 = select i1 %61, i64 %62, i64 0
  store i64 0, ptr %2, align 8, !tbaa !9
  store i64 0, ptr %3, align 8, !tbaa !9
  %64 = call i64 @repo_read(ptr noundef nonnull %2, ptr noundef nonnull %3, i64 noundef %22, i64 noundef %49, i64 noundef 8101820097204584448, i64 noundef 0) #4
  %65 = load volatile i32, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %66 = add i32 %65, 1
  store volatile i32 %66, ptr inttoptr (i64 9637684 to ptr), align 4, !tbaa !17
  %67 = icmp eq i64 %64, 0
  %68 = load i64, ptr %2, align 8
  %69 = trunc i64 %68 to i32
  %70 = select i1 %67, i32 %69, i32 255
  %71 = icmp eq i64 %55, 5
  br i1 %71, label %72, label %88

72:                                               ; preds = %54
  %73 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !22
  %74 = add i32 %73, 1
  store volatile i32 %74, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !22
  %75 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !22
  %76 = icmp eq i32 %75, 1
  br i1 %76, label %77, label %80

77:                                               ; preds = %72
  store volatile i8 %35, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %78 = trunc i64 %46 to i8
  store volatile i8 %78, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %79 = trunc i32 %70 to i8
  store volatile i8 %79, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  store volatile i64 %43, ptr inttoptr (i64 9637728 to ptr), align 32, !tbaa !23
  store volatile i64 %63, ptr inttoptr (i64 9637736 to ptr), align 8, !tbaa !24
  br label %80

80:                                               ; preds = %77, %72
  br i1 %34, label %81, label %84

81:                                               ; preds = %80
  %82 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !25
  %83 = or i8 %82, 1
  store volatile i8 %83, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !25
  br label %84

84:                                               ; preds = %81, %80
  br i1 %44, label %85, label %98

85:                                               ; preds = %84
  %86 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !25
  %87 = or i8 %86, 2
  store volatile i8 %87, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !25
  br label %98

88:                                               ; preds = %54
  %89 = icmp eq i64 %55, 0
  %90 = select i1 %44, i1 %89, i1 false
  %91 = icmp eq i32 %70, 2
  %92 = select i1 %90, i1 %91, i1 false
  br i1 %92, label %93, label %98

93:                                               ; preds = %88
  %94 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !26
  %95 = icmp eq i32 %94, 0
  br i1 %95, label %96, label %98

96:                                               ; preds = %93
  store volatile i32 1, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !26
  store volatile i8 4, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %97 = trunc i64 %46 to i8
  store volatile i8 %97, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  store volatile i8 2, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  store volatile i64 %43, ptr inttoptr (i64 9637712 to ptr), align 16, !tbaa !27
  store volatile i64 %63, ptr inttoptr (i64 9637720 to ptr), align 8, !tbaa !28
  br label %98

98:                                               ; preds = %96, %93, %88, %85, %84, %48
  %99 = add nuw nsw i64 %46, 1
  br label %45, !llvm.loop !29

100:                                              ; preds = %45, %30, %27
  %101 = add nuw nsw i64 %11, 1
  br label %10, !llvm.loop !31

102:                                              ; preds = %13
  %103 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %104 = or i32 %103, 8
  store volatile i32 %104, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %105

105:                                              ; preds = %13, %102
  store volatile i64 0, ptr inttoptr (i64 9637752 to ptr), align 8, !tbaa !32
  store volatile i32 0, ptr inttoptr (i64 9637708 to ptr), align 4, !tbaa !33
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #3
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #3
  %106 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %107 = or i32 %106, 2
  store volatile i32 %107, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  br label %108

108:                                              ; preds = %105, %1
  %109 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %110 = and i32 %109, 2
  %111 = icmp eq i32 %110, 0
  br i1 %111, label %266, label %112

112:                                              ; preds = %108
  %113 = trunc i64 %0 to i32
  %114 = and i32 %113, 3
  switch i32 %114, label %265 [
    i32 0, label %115
    i32 1, label %132
    i32 2, label %154
    i32 3, label %221
  ]

115:                                              ; preds = %112
  %116 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %117 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !18
  %118 = and i32 %116, 4
  %119 = icmp eq i32 %118, 0
  br i1 %119, label %129, label %120

120:                                              ; preds = %115
  %121 = trunc i64 %117 to i32
  %122 = add i32 %121, 17
  %123 = icmp ult i32 %122, 18
  br i1 %123, label %124, label %129

124:                                              ; preds = %120
  %125 = zext nneg i32 %122 to i64
  %126 = getelementptr inbounds nuw [2 x i8], ptr @switch.table.s4_menu, i64 %125
  %127 = load i16, ptr %126, align 2
  %128 = zext i16 %127 to i64
  br label %129

129:                                              ; preds = %120, %124, %115
  %130 = phi i64 [ 0, %115 ], [ %128, %124 ], [ 704, %120 ]
  %131 = getelementptr inbounds nuw i8, ptr @labels_page_a, i64 %130
  br label %266

132:                                              ; preds = %112
  %133 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %134 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !18
  %135 = and i32 %133, 4
  %136 = icmp eq i32 %135, 0
  br i1 %136, label %149, label %137

137:                                              ; preds = %132
  %138 = trunc i64 %134 to i32
  %139 = icmp ugt i32 %138, -257
  br i1 %139, label %140, label %142

140:                                              ; preds = %137
  %141 = and i32 %138, 255
  br label %149

142:                                              ; preds = %137
  %143 = icmp ult i32 %138, 256
  br i1 %143, label %144, label %146

144:                                              ; preds = %142
  %145 = or disjoint i32 %138, 256
  br label %149

146:                                              ; preds = %142
  %147 = lshr i32 %138, 28
  %148 = or disjoint i32 %147, 512
  br label %149

149:                                              ; preds = %132, %140, %144, %146
  %150 = phi i32 [ 528, %132 ], [ %141, %140 ], [ %145, %144 ], [ %148, %146 ]
  %151 = shl nuw nsw i32 %150, 6
  %152 = zext nneg i32 %151 to i64
  %153 = getelementptr inbounds nuw i8, ptr @labels_page_b, i64 %152
  br label %266

154:                                              ; preds = %112
  %155 = load volatile i32, ptr inttoptr (i64 9637672 to ptr), align 8, !tbaa !22
  %156 = icmp eq i32 %155, 0
  br i1 %156, label %179, label %157

157:                                              ; preds = %154
  %158 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %159 = icmp eq i8 %158, 4
  br i1 %159, label %160, label %166

160:                                              ; preds = %157
  %161 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %162 = icmp eq i8 %161, 2
  br i1 %162, label %163, label %166

163:                                              ; preds = %160
  %164 = load volatile i8, ptr inttoptr (i64 9637698 to ptr), align 2, !tbaa !13
  %165 = icmp eq i8 %164, 0
  br i1 %165, label %179, label %166

166:                                              ; preds = %163, %160, %157
  %167 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %168 = icmp eq i8 %167, 5
  br i1 %168, label %169, label %172

169:                                              ; preds = %166
  %170 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %171 = icmp eq i8 %170, 0
  br i1 %171, label %179, label %172

172:                                              ; preds = %169, %166
  %173 = load volatile i8, ptr inttoptr (i64 9637696 to ptr), align 64, !tbaa !11
  %174 = icmp eq i8 %173, 4
  br i1 %174, label %175, label %178

175:                                              ; preds = %172
  %176 = load volatile i8, ptr inttoptr (i64 9637697 to ptr), align 1, !tbaa !12
  %177 = icmp eq i8 %176, 2
  br i1 %177, label %179, label %178

178:                                              ; preds = %175, %172
  br label %179

179:                                              ; preds = %178, %175, %169, %163, %154
  %180 = phi i64 [ 0, %154 ], [ 901, %163 ], [ 1802, %169 ], [ 3604, %178 ], [ 2703, %175 ]
  %181 = load volatile i32, ptr inttoptr (i64 9637676 to ptr), align 4, !tbaa !26
  %182 = icmp eq i32 %181, 0
  br i1 %182, label %215, label %183

183:                                              ; preds = %179
  %184 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %185 = icmp ult i8 %184, 8
  br i1 %185, label %186, label %190

186:                                              ; preds = %183
  %187 = load volatile i8, ptr inttoptr (i64 9637700 to ptr), align 4, !tbaa !14
  %188 = zext i8 %187 to i64
  %189 = mul nuw nsw i64 %188, 5
  br label %190

190:                                              ; preds = %186, %183
  %191 = phi i64 [ %189, %186 ], [ 40, %183 ]
  %192 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %193 = icmp ult i8 %192, 4
  br i1 %193, label %194, label %197

194:                                              ; preds = %190
  %195 = load volatile i8, ptr inttoptr (i64 9637701 to ptr), align 1, !tbaa !15
  %196 = zext i8 %195 to i64
  br label %197

197:                                              ; preds = %194, %190
  %198 = phi i64 [ %196, %194 ], [ 4, %190 ]
  %199 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %200 = icmp ult i8 %199, 4
  br i1 %200, label %201, label %204

201:                                              ; preds = %197
  %202 = load volatile i8, ptr inttoptr (i64 9637702 to ptr), align 2, !tbaa !16
  %203 = zext i8 %202 to i64
  br label %204

204:                                              ; preds = %201, %197
  %205 = phi i64 [ %203, %201 ], [ 4, %197 ]
  %206 = load volatile i8, ptr inttoptr (i64 9637703 to ptr), align 1, !tbaa !25
  %207 = and i8 %206, 3
  %208 = zext nneg i8 %207 to i64
  %209 = add nuw nsw i64 %198, %191
  %210 = mul nuw nsw i64 %209, 5
  %211 = add nuw nsw i64 %205, %210
  %212 = shl nuw nsw i64 %211, 2
  %213 = or disjoint i64 %212, 1
  %214 = add nuw nsw i64 %213, %208
  br label %215

215:                                              ; preds = %179, %204
  %216 = phi i64 [ %214, %204 ], [ 0, %179 ]
  %217 = add nuw nsw i64 %216, %180
  %218 = shl nuw nsw i64 %217, 6
  %219 = and i64 %218, 4294967232
  %220 = getelementptr inbounds nuw i8, ptr @labels_page_c, i64 %219
  br label %266

221:                                              ; preds = %112
  %222 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %223 = load volatile i32, ptr inttoptr (i64 9637664 to ptr), align 32, !tbaa !6
  %224 = load volatile i64, ptr inttoptr (i64 9637744 to ptr), align 16, !tbaa !18
  %225 = and i32 %222, 4
  %226 = icmp eq i32 %225, 0
  br i1 %226, label %236, label %227

227:                                              ; preds = %221
  %228 = trunc i64 %224 to i32
  %229 = add i32 %228, 17
  %230 = icmp ult i32 %229, 18
  br i1 %230, label %231, label %236

231:                                              ; preds = %227
  %232 = zext nneg i32 %229 to i64
  %233 = getelementptr inbounds nuw [4 x i8], ptr @switch.table.s4_menu.1, i64 %232
  %234 = load i32, ptr %233, align 4
  %235 = zext i32 %234 to i64
  br label %236

236:                                              ; preds = %227, %231, %221
  %237 = phi i64 [ 0, %221 ], [ %235, %231 ], [ 67584, %227 ]
  %238 = load volatile i64, ptr inttoptr (i64 9637752 to ptr), align 8, !tbaa !32
  %239 = and i32 %223, 16
  %240 = icmp eq i32 %239, 0
  br i1 %240, label %250, label %241

241:                                              ; preds = %236
  %242 = trunc i64 %238 to i32
  %243 = add i32 %242, 17
  %244 = icmp ult i32 %243, 18
  br i1 %244, label %245, label %250

245:                                              ; preds = %241
  %246 = zext nneg i32 %243 to i64
  %247 = getelementptr inbounds nuw [2 x i8], ptr @switch.table.s4_menu.2, i64 %246
  %248 = load i16, ptr %247, align 2
  %249 = zext i16 %248 to i64
  br label %250

250:                                              ; preds = %241, %245, %236
  %251 = phi i64 [ 0, %236 ], [ %249, %245 ], [ 5632, %241 ]
  %252 = load volatile i32, ptr inttoptr (i64 9637688 to ptr), align 8, !tbaa !20
  %253 = add i32 %252, 6
  %254 = icmp ult i32 %253, 7
  br i1 %254, label %255, label %260

255:                                              ; preds = %250
  %256 = zext nneg i32 %253 to i64
  %257 = getelementptr inbounds nuw [2 x i8], ptr @switch.table.s4_menu.3, i64 %256
  %258 = load i16, ptr %257, align 2
  %259 = zext i16 %258 to i64
  br label %260

260:                                              ; preds = %250, %255
  %261 = phi i64 [ %259, %255 ], [ 448, %250 ]
  %262 = getelementptr inbounds nuw i8, ptr @labels_page_d, i64 %237
  %263 = getelementptr inbounds nuw i8, ptr %262, i64 %251
  %264 = getelementptr inbounds nuw i8, ptr %263, i64 %261
  br label %266

265:                                              ; preds = %112
  unreachable

266:                                              ; preds = %129, %149, %215, %260, %108
  %267 = phi ptr [ inttoptr (i64 3165888 to ptr), %108 ], [ %264, %260 ], [ %131, %129 ], [ %153, %149 ], [ %220, %215 ]
  ret ptr %267
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: minsize optsize
declare i64 @repo_read(ptr noundef, ptr noundef, i64 noundef, i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: minsize optsize
declare i64 @lv1_open_device(i64 noundef, i64 noundef, i64 noundef) local_unnamed_addr #2

attributes #0 = { minsize nounwind optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { minsize optsize "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="970" "target-features"="+64bit-support,+fpu,+fres,+frsqrte,+fsqrt,+mfocrf,+stfiwx,-altivec,-crypto,-direct-move,-float128,-hard-float,-mma,-paired-vector-memops,-power10-vector,-power8-vector,-power9-vector,-vsx" "use-soft-float"="true" }
attributes #3 = { nounwind }
attributes #4 = { minsize nobuiltin nounwind optsize "no-builtins" }

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
!9 = !{!8, !8, i64 0}
!10 = !{!7, !4, i64 35}
!11 = !{!7, !4, i64 32}
!12 = !{!7, !4, i64 33}
!13 = !{!7, !4, i64 34}
!14 = !{!7, !4, i64 36}
!15 = !{!7, !4, i64 37}
!16 = !{!7, !4, i64 38}
!17 = !{!7, !3, i64 20}
!18 = !{!7, !8, i64 80}
!19 = !{!7, !3, i64 40}
!20 = !{!7, !3, i64 24}
!21 = !{!7, !3, i64 4}
!22 = !{!7, !3, i64 8}
!23 = !{!7, !8, i64 64}
!24 = !{!7, !8, i64 72}
!25 = !{!7, !4, i64 39}
!26 = !{!7, !3, i64 12}
!27 = !{!7, !8, i64 48}
!28 = !{!7, !8, i64 56}
!29 = distinct !{!29, !30}
!30 = !{!"llvm.loop.mustprogress"}
!31 = distinct !{!31, !30}
!32 = !{!7, !8, i64 88}
!33 = !{!7, !3, i64 44}
