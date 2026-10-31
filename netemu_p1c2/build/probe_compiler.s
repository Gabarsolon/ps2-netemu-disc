	.abiversion 2
	.file	"probe.c"
	.text
	.globl	s4_menu
	.p2align	2
	.type	s4_menu,@function
s4_menu:
.Lfunc_begin0:
.Lfunc_gep0:
	addis 2, 12, .TOC.-.Lfunc_gep0@ha
	addi 2, 2, .TOC.-.Lfunc_gep0@l
.Lfunc_lep0:
	.localentry	s4_menu, .Lfunc_lep0-.Lfunc_gep0
	mfocrf 12, 32
	stw 12, 8(1)
	mflr 0
	stdu 1, -240(1)
	std 0, 256(1)
	std 14, 96(1)
	std 15, 104(1)
	std 16, 112(1)
	std 17, 120(1)
	std 18, 128(1)
	std 19, 136(1)
	std 20, 144(1)
	std 21, 152(1)
	std 22, 160(1)
	std 23, 168(1)
	std 24, 176(1)
	std 25, 184(1)
	mr	25, 3
	lis 3, 147
	ori 21, 3, 3872
	std 26, 192(1)
	std 27, 200(1)
	std 28, 208(1)
	std 29, 216(1)
	std 30, 224(1)
	std 31, 232(1)
	lwz 4, 3872(3)
	andi. 4, 4, 1
	bc 12, 1, .LBB0_46
	lwz 3, 0(21)
	li 30, 0
	li 4, 3
	li 5, 0
	ori 3, 3, 1
	stw 3, 0(21)
	li 3, -1
	std 30, 88(1)
	std 30, 80(1)
	stb 3, 40(21)
	stb 3, 41(21)
	stb 3, 42(21)
	stb 3, 43(21)
	stb 3, 44(21)
	stb 3, 45(21)
	li 3, 4096
	stw 30, 20(21)
	std 30, 80(21)
	bl native_alloc
	nop
	mr	29, 3
	bl arena_rw
	cmplwi	3, 0
	beq	0, .LBB0_33
	li 3, 4097
	mtctr 3
	addi 3, 29, -1
	bdz .LBB0_4
.LBB0_3:
	addi 4, 3, 1
	stb 30, 1(3)
	mr	3, 4
	bdnz .LBB0_3
.LBB0_4:
	addi 8, 21, 48
	lis 3, 29817
	std 25, 40(1)
	ori 3, 3, 28773
	li 4, 6745
	std 8, 72(1)
	addi 8, 21, 64
	rldic 27, 3, 32, 1
	std 8, 56(1)
	lis 5, 98
	lis 6, 50
	lis 7, 7195
	rldic 28, 4, 50, 1
	std 29, 32(1)
	ori 4, 5, 30067
	ori 5, 6, 12987
	std 29, 32(21)
	ori 6, 7, 56477
	rldic 4, 4, 40, 1
	li 20, 0
	addi 26, 1, 88
	lwz 3, 0(21)
	addi 25, 1, 80
	addi 18, 21, 56
	ori 3, 3, 4
	std 4, 64(1)
	rldic 30, 5, 41, 1
	rldic 24, 6, 34, 1
	li 17, 0
	stw 3, 0(21)
	addi 3, 21, 72
	std 3, 48(1)
.LBB0_5:
	cmpldi	17, 16
	beq	0, .LBB0_31
	ld 3, 64(1)
	mr	4, 25
	mr	6, 27
	li 7, 0
	li 8, 0
	std 20, 88(1)
	or 23, 17, 3
	mr	3, 26
	mr	5, 23
	std 20, 80(1)
	bl repo_read
	nop
	lwz 4, 4(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 4(21)
	beq	0, .LBB0_10
	lwz 4, 16(21)
	cmplwi	4, 0
	bne	0, .LBB0_9
	stw 3, 16(21)
.LBB0_9:
	addi 17, 17, 1
	b .LBB0_5
.LBB0_10:
	li 16, 0
	mr	3, 26
	std 16, 88(1)
	mr	4, 25
	mr	5, 23
	mr	6, 28
	li 7, 0
	std 16, 80(1)
	li 8, 0
	bl repo_read
	nop
	lwz 4, 4(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 4(21)
	beq	0, .LBB0_12
	li 15, 0
	b .LBB0_13
.LBB0_12:
	ld 15, 88(1)
.LBB0_13:
	cmpdi 2, 17, 4
	li 14, 17
.LBB0_14:
	addi 14, 14, -1
	cmpldi	14, 0
	bc 4, 1, .LBB0_9
	add 22, 16, 30
	mr	3, 26
	std 20, 88(1)
	mr	4, 25
	mr	5, 23
	std 20, 80(1)
	mr	6, 22
	mr	7, 27
	li 8, 0
	bl repo_read
	nop
	lwz 4, 4(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 4(21)
	beq	0, .LBB0_17
.LBB0_16:
	addi 16, 16, 1
	b .LBB0_14
.LBB0_17:
	li 19, 0
	mr	3, 26
	ld 31, 88(1)
	mr	4, 25
	mr	5, 23
	std 19, 88(1)
	mr	6, 22
	mr	7, 28
	li 8, 0
	std 19, 80(1)
	bl repo_read
	nop
	lwz 4, 4(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 4(21)
	beq	0, .LBB0_19
	li 29, 0
	b .LBB0_20
.LBB0_19:
	ld 29, 88(1)
.LBB0_20:
	mr	3, 26
	mr	4, 25
	std 19, 88(1)
	mr	5, 23
	mr	6, 22
	std 19, 80(1)
	mr	7, 24
	li 8, 0
	bl repo_read
	nop
	lwz 4, 4(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 4(21)
	beq	0, .LBB0_22
	li 3, 255
	b .LBB0_23
.LBB0_22:
	lwz 3, 92(1)
.LBB0_23:
	cmpldi	31, 5
	bne	0, .LBB0_26
	lwz 4, 8(21)
	addi 4, 4, 1
	stw 4, 8(21)
	lwz 4, 8(21)
	cmplwi	4, 1
	bne	0, .LBB0_16
	stb 17, 40(21)
	mr	4, 18
	stb 16, 41(21)
	stb 3, 42(21)
	ld 3, 72(1)
	b .LBB0_30
.LBB0_26:
	cmpdi	31, 0
	crand 20, 10, 2
	bc 4, 20, .LBB0_16
	cmpwi	3, 2
	bc 4, 2, .LBB0_16
	lwz 3, 12(21)
	cmplwi	3, 0
	bne	0, .LBB0_16
	li 3, 1
	stw 3, 12(21)
	li 3, 4
	stb 3, 43(21)
	li 3, 2
	stb 16, 44(21)
	stb 3, 45(21)
	ld 3, 56(1)
	ld 4, 48(1)
.LBB0_30:
	std 15, 0(3)
	std 29, 0(4)
	b .LBB0_16
.LBB0_31:
	lbz 3, 40(21)
	cmplwi	3, 255
	beq	0, .LBB0_34
	lbz 4, 40(21)
	b .LBB0_35
.LBB0_33:
	lwz 3, 0(21)
	ori 3, 3, 8
	stw 3, 0(21)
	b .LBB0_45
.LBB0_34:
	li 4, 4
.LBB0_35:
	ld 25, 40(1)
	ld 30, 32(1)
	lbz 3, 41(21)
	cmplwi	3, 255
	beq	0, .LBB0_37
	lbz 5, 41(21)
	b .LBB0_38
.LBB0_37:
	li 5, 2
.LBB0_38:
	mr	3, 30
	bl dump_node
	lbz 3, 43(21)
	cmplwi	3, 255
	beq	0, .LBB0_40
	lbz 4, 43(21)
	b .LBB0_41
.LBB0_40:
	li 4, 4
.LBB0_41:
	lbz 3, 44(21)
	cmplwi	3, 255
	beq	0, .LBB0_43
	lbz 5, 44(21)
	b .LBB0_44
.LBB0_43:
	li 5, 3
.LBB0_44:
	addi 3, 30, 480
	bl dump_node
	lis 4, 1122
	addi 3, 30, 960
	ori 4, 4, 30067
	mr	5, 27
	rotldi	26, 4, 40
	li 6, 0
	mr	4, 26
	li 7, 0
	bl read_one_field
	addi 3, 30, 984
	mr	4, 26
	mr	5, 28
	li 6, 0
	li 7, 0
	bl read_one_field
	lis 4, 28277
	addi 3, 30, 1008
	ori 4, 4, 27999
	li 6, 0
	rldic 4, 4, 32, 1
	li 7, 0
	oris 4, 4, 25701
	ori 5, 4, 30208
	mr	4, 26
	bl read_one_field
.LBB0_45:
	lwz 3, 0(21)
	ori 3, 3, 2
	stw 3, 0(21)
.LBB0_46:
	lwz 3, 0(21)
	andi. 3, 3, 8
	lis 3, 48
	ori 28, 3, 20160
	bne	0, .LBB0_119
	lwz 3, 0(21)
	andi. 3, 3, 2
	beq	0, .LBB0_119
	bl get_arena
	cmpldi	3, 0
	beq	0, .LBB0_119
	mr	29, 3
	bl native_clock
	nop
	ld 4, 80(21)
	lis 5, 1826
	ori 5, 5, 31264
	cmpdi 5, 4, 0
	sub	6, 3, 4
	cmpld	3, 4
	cmpld 1, 6, 5
	bc 12, 22, .LBB0_52
	crand 20, 1, 5
	bc 4, 20, .LBB0_52
	lwz 4, 20(21)
	addi 4, 4, 1
	stw 4, 20(21)
.LBB0_52:
	cmpldi	25, 8
	std 3, 80(21)
	blt	0, .LBB0_54
	li 25, 8
.LBB0_54:
	lwz 3, 20(21)
	li 4, 24
	mulli 3, 3, 9
	add 3, 3, 25
	divwu 4, 3, 4
	mulli 4, 4, 24
	sub	3, 3, 4
	cmplwi	3, 23
	beq	0, .LBB0_117
	cmplwi	3, 1
	beq	0, .LBB0_115
	cmplwi	3, 2
	beq	0, .LBB0_109
	cmplwi	3, 3
	beq	0, .LBB0_107
	cmplwi	3, 4
	beq	0, .LBB0_116
	cmplwi	3, 5
	beq	0, .LBB0_112
	cmplwi	3, 6
	beq	0, .LBB0_106
	cmplwi	3, 7
	beq	0, .LBB0_78
	cmplwi	3, 8
	beq	0, .LBB0_85
	cmplwi	3, 9
	beq	0, .LBB0_79
	cmplwi	3, 10
	beq	0, .LBB0_110
	cmplwi	3, 11
	beq	0, .LBB0_82
	cmplwi	3, 12
	beq	0, .LBB0_80
	cmplwi	3, 13
	beq	0, .LBB0_113
	cmplwi	3, 14
	beq	0, .LBB0_83
	cmplwi	3, 15
	beq	0, .LBB0_114
	cmplwi	3, 16
	beq	0, .LBB0_87
	cmplwi	3, 17
	beq	0, .LBB0_111
	cmplwi	3, 18
	beq	0, .LBB0_108
	cmplwi	3, 19
	beq	0, .LBB0_81
	cmplwi	3, 20
	beq	0, .LBB0_86
	cmplwi	3, 21
	beq	0, .LBB0_84
	cmplwi	3, 22
	bne	0, .LBB0_88
	ld 3, 744(29)
	ld 4, 752(29)
	bl map_field_idx
	ld 4, .LC0@toc(2)
	b .LBB0_118
.LBB0_78:
	ld 3, 72(29)
	ld 4, 80(29)
	bl map_blk_idx
	ld 4, .LC1@toc(2)
	b .LBB0_118
.LBB0_79:
	ld 3, 96(29)
	ld 4, 104(29)
	bl map_field_idx
	ld 4, .LC2@toc(2)
	b .LBB0_118
.LBB0_80:
	ld 3, 600(29)
	ld 4, 608(29)
	bl map_field_idx
	ld 4, .LC3@toc(2)
	b .LBB0_118
.LBB0_81:
	ld 3, 336(29)
	ld 4, 344(29)
	bl map_field_idx
	ld 4, .LC4@toc(2)
	b .LBB0_118
.LBB0_82:
	ld 3, 120(29)
	ld 4, 128(29)
	bl map_field_idx
	ld 4, .LC5@toc(2)
	b .LBB0_118
.LBB0_83:
	ld 3, 624(29)
	ld 4, 632(29)
	bl map_field_idx
	ld 4, .LC6@toc(2)
	b .LBB0_118
.LBB0_84:
	ld 3, 264(29)
	ld 4, 272(29)
	bl map_field_idx
	ld 4, .LC7@toc(2)
	b .LBB0_118
.LBB0_85:
	ld 3, 552(29)
	ld 4, 560(29)
	bl map_blk_idx
	ld 4, .LC8@toc(2)
	b .LBB0_118
.LBB0_86:
	ld 3, 816(29)
	ld 4, 824(29)
	bl map_field_idx
	ld 4, .LC9@toc(2)
	b .LBB0_118
.LBB0_87:
	ld 3, 648(29)
	ld 4, 656(29)
	bl map_field_idx
	ld 4, .LC10@toc(2)
	b .LBB0_118
.LBB0_88:
	lwz 3, 8(21)
	cmplwi	3, 4
	li 3, 8
	bgt	0, .LBB0_90
	lwz 3, 8(21)
	slwi 3, 3, 1
.LBB0_90:
	lwz 5, 12(21)
	li 6, 15
	lbz 4, 40(21)
	cmplwi	4, 15
	li 4, 15
	bgt	0, .LBB0_92
	lbz 6, 40(21)
.LBB0_92:
	lbz 7, 41(21)
	cntlzw	5, 5
	cmplwi	7, 15
	bgt	0, .LBB0_94
	lbz 4, 41(21)
.LBB0_94:
	lbz 7, 42(21)
	cmplwi	7, 2
	srwi 7, 5, 5
	li 5, 3
	bgt	0, .LBB0_96
	lbz 5, 42(21)
.LBB0_96:
	ld 8, 48(21)
	xori 7, 7, 1
	cmpldi	8, 4
	bne	0, .LBB0_98
	ld 8, 56(21)
	cmpldi	8, 2
	li 8, 0
	beq	0, .LBB0_103
.LBB0_98:
	ld 8, 48(21)
	cmpld	8, 6
	bne	0, .LBB0_100
	ld 6, 56(21)
	li 8, 4
	cmpld	6, 4
	beq	0, .LBB0_103
.LBB0_100:
	ld 4, 48(21)
	cmpldi	4, 1280
	bne	0, .LBB0_102
	ld 4, 56(21)
	li 8, 8
	cmpldi	4, 1281
	beq	0, .LBB0_103
.LBB0_102:
	li 8, 12
.LBB0_103:
	or 3, 3, 7
	slwi 3, 3, 4
	add 3, 5, 3
	add 3, 3, 8
	cmplwi	3, 159
	blt	0, .LBB0_105
	li 3, 159
.LBB0_105:
	ld 4, .LC11@toc(2)
	b .LBB0_118
.LBB0_106:
	ld 3, 528(29)
	ld 4, 536(29)
	bl map_field_idx
	ld 4, .LC12@toc(2)
	b .LBB0_118
.LBB0_107:
	ld 3, 24(29)
	ld 4, 32(29)
	bl map_field_idx
	ld 4, .LC13@toc(2)
	b .LBB0_118
.LBB0_108:
	ld 3, 720(29)
	ld 4, 728(29)
	bl map_field_idx
	ld 4, .LC14@toc(2)
	b .LBB0_118
.LBB0_109:
	ld 3, 480(29)
	ld 4, 488(29)
	bl map_field_idx
	ld 4, .LC15@toc(2)
	b .LBB0_118
.LBB0_110:
	ld 3, 576(29)
	ld 4, 584(29)
	bl map_field_idx
	ld 4, .LC16@toc(2)
	b .LBB0_118
.LBB0_111:
	ld 3, 240(29)
	ld 4, 248(29)
	bl map_field_idx
	ld 4, .LC17@toc(2)
	b .LBB0_118
.LBB0_112:
	ld 3, 48(29)
	ld 4, 56(29)
	bl map_field_idx
	ld 4, .LC18@toc(2)
	b .LBB0_118
.LBB0_113:
	ld 3, 144(29)
	ld 4, 152(29)
	bl map_field_idx
	ld 4, .LC19@toc(2)
	b .LBB0_118
.LBB0_114:
	ld 3, 168(29)
	ld 4, 176(29)
	bl map_field_idx
	ld 4, .LC20@toc(2)
	b .LBB0_118
.LBB0_115:
	ld 3, 0(29)
	ld 4, 8(29)
	bl map_field_idx
	ld 4, .LC21@toc(2)
	b .LBB0_118
.LBB0_116:
	ld 3, 504(29)
	ld 4, 512(29)
	bl map_field_idx
	ld 4, .LC22@toc(2)
	b .LBB0_118
.LBB0_117:
	ld 3, 1008(29)
	ld 4, 1016(29)
	bl map_field_idx
	ld 4, .LC23@toc(2)
.LBB0_118:
	rlwinm 3, 3, 5, 0, 26
	add 28, 4, 3
.LBB0_119:
	mr	3, 28
	ld 31, 232(1)
	ld 30, 224(1)
	ld 29, 216(1)
	ld 28, 208(1)
	ld 27, 200(1)
	ld 26, 192(1)
	ld 25, 184(1)
	ld 24, 176(1)
	ld 23, 168(1)
	ld 22, 160(1)
	ld 21, 152(1)
	ld 20, 144(1)
	ld 19, 136(1)
	ld 18, 128(1)
	ld 17, 120(1)
	ld 16, 112(1)
	ld 15, 104(1)
	ld 14, 96(1)
	addi 1, 1, 240
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	blr
	.long	0
	.quad	0
.Lfunc_end0:
	.size	s4_menu, .Lfunc_end0-.Lfunc_begin0

	.p2align	2
	.type	get_arena,@function
get_arena:
.Lfunc_begin1:
.Lfunc_gep1:
	addis 2, 12, .TOC.-.Lfunc_gep1@ha
	addi 2, 2, .TOC.-.Lfunc_gep1@l
.Lfunc_lep1:
	.localentry	get_arena, .Lfunc_lep1-.Lfunc_gep1
	mflr 0
	std 30, -16(1)
	stdu 1, -48(1)
	std 0, 64(1)
	lis 3, 147
	ld 30, 3904(3)
	mr	3, 30
	bl arena_rw
	cmplwi	3, 0
	li 3, 0
	beq	0, .LBB1_2
	mr	3, 30
.LBB1_2:
	addi 1, 1, 48
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	blr
	.long	0
	.quad	0
.Lfunc_end1:
	.size	get_arena, .Lfunc_end1-.Lfunc_begin1

	.p2align	2
	.type	map_field_idx,@function
map_field_idx:
.Lfunc_begin2:
	cmpdi	3, -6
	beq	0, .LBB2_11
	cmpdi	3, -5
	beq	0, .LBB2_14
	cmpldi	3, 0
	beq	0, .LBB2_13
	cmpdi	3, -3
	beq	0, .LBB2_8
	cmpdi	3, -2
	beq	0, .LBB2_10
	cmpdi	3, -1
	beq	0, .LBB2_9
	cmpdi	3, -4
	bne	0, .LBB2_12
	li 3, 1
	b .LBB2_15
.LBB2_8:
	li 3, 2
	b .LBB2_15
.LBB2_9:
	li 3, 4
	b .LBB2_15
.LBB2_10:
	li 3, 5
	b .LBB2_15
.LBB2_11:
	li 3, 0
	b .LBB2_15
.LBB2_12:
	li 3, 6
	b .LBB2_15
.LBB2_13:
	clrlwi	3, 4, 24
	addi 3, 3, 7
	b .LBB2_15
.LBB2_14:
	li 3, 3
.LBB2_15:
	clrldi	3, 3, 32
	blr
	.long	0
	.quad	0
.Lfunc_end2:
	.size	map_field_idx, .Lfunc_end2-.Lfunc_begin2

	.p2align	2
	.type	map_blk_idx,@function
map_blk_idx:
.Lfunc_begin3:
	cmpdi	3, -6
	beq	0, .LBB3_17
	cmpdi	3, -5
	beq	0, .LBB3_6
	cmpldi	3, 0
	beq	0, .LBB3_8
	cmpdi	3, -3
	beq	0, .LBB3_7
	cmpdi	3, -4
	bne	0, .LBB3_16
	li 3, 1
	b .LBB3_18
.LBB3_6:
	li 3, 3
	b .LBB3_18
.LBB3_7:
	li 3, 2
	b .LBB3_18
.LBB3_8:
	cmpldi	4, 0
	beq	0, .LBB3_22
	cmpldi	4, 4096
	beq	0, .LBB3_25
	cmpldi	4, 1024
	beq	0, .LBB3_24
	cmpldi	4, 2048
	beq	0, .LBB3_19
	cmpldi	4, 2064
	beq	0, .LBB3_21
	cmpldi	4, 2352
	beq	0, .LBB3_20
	cmpldi	4, 512
	bne	0, .LBB3_23
	li 3, 6
	b .LBB3_18
.LBB3_16:
	li 3, 4
	b .LBB3_18
.LBB3_17:
	li 3, 0
.LBB3_18:
	clrldi	3, 3, 32
	blr
.LBB3_19:
	li 3, 8
	b .LBB3_18
.LBB3_20:
	li 3, 10
	b .LBB3_18
.LBB3_21:
	li 3, 11
	b .LBB3_18
.LBB3_22:
	li 3, 5
	b .LBB3_18
.LBB3_23:
	rlwinm 3, 4, 24, 24, 31
	addi 3, 3, 12
	b .LBB3_18
.LBB3_24:
	li 3, 7
	b .LBB3_18
.LBB3_25:
	li 3, 9
	b .LBB3_18
	.long	0
	.quad	0
.Lfunc_end3:
	.size	map_blk_idx, .Lfunc_end3-.Lfunc_begin3

	.p2align	2
	.type	arena_rw,@function
arena_rw:
.Lfunc_begin4:
	lis 4, 147
	ld 5, 18816(4)
	rldicl 4, 5, 36, 5
	rotldi	4, 4, 28
	xoris 4, 4, 32768
	cmpldi	4, 0
	li 4, 0
	bne	0, .LBB4_4
	lis 6, 581
	ld 6, 26040(6)
	cmpld	6, 5
	bne	0, .LBB4_4
	lis 6, 580
	oris 7, 5, 2
	ld 6, 25992(6)
	clrldi	8, 3, 58
	cmpld 1, 3, 7
	xor 6, 6, 7
	or. 6, 8, 6
	crorc 20, 4, 2
	bc 12, 20, .LBB4_4
	addi 3, 3, 4096
	oris 4, 5, 6
	subc	4, 4, 3
	subfe 3, 3, 3
	addi 4, 3, 1
.LBB4_4:
	clrldi	3, 4, 32
	blr
	.long	0
	.quad	0
.Lfunc_end4:
	.size	arena_rw, .Lfunc_end4-.Lfunc_begin4

	.p2align	2
	.type	dump_node,@function
dump_node:
.Lfunc_begin5:
.Lfunc_gep5:
	addis 2, 12, .TOC.-.Lfunc_gep5@ha
	addi 2, 2, .TOC.-.Lfunc_gep5@l
.Lfunc_lep5:
	.localentry	dump_node, .Lfunc_lep5-.Lfunc_gep5
	mflr 0
	std 24, -64(1)
	std 25, -56(1)
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -96(1)
	mr	30, 3
	lis 3, 98
	std 0, 112(1)
	ori 3, 3, 30067
	lis 6, 50
	rldic 3, 3, 40, 1
	ori 6, 6, 12987
	or 29, 4, 3
	lis 3, 29817
	rldic 6, 6, 41, 1
	ori 3, 3, 28773
	or 28, 5, 6
	rldic 27, 3, 32, 1
	mr	3, 30
	mr	4, 29
	mr	5, 28
	mr	6, 27
	li 7, 0
	bl read_one_field
	li 4, 6745
	addi 3, 30, 24
	rldic 6, 4, 50, 1
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	lis 4, 7195
	addi 3, 30, 48
	ori 4, 4, 56477
	mr	5, 28
	rldic 6, 4, 34, 1
	mr	4, 29
	li 7, 0
	bl read_one_field
	lis 4, 25196
	addi 3, 30, 72
	ori 4, 4, 27487
	mr	5, 28
	rldic 4, 4, 32, 1
	li 7, 0
	oris 4, 4, 29545
	ori 6, 4, 31333
	mr	4, 29
	bl read_one_field
	lis 4, 7063
	addi 3, 30, 96
	ori 4, 4, 55451
	mr	5, 28
	rldic 4, 4, 34, 1
	li 7, 0
	oris 4, 4, 28515
	ori 6, 4, 27507
	mr	4, 29
	bl read_one_field
	lis 4, 28255
	addi 3, 30, 120
	ori 4, 4, 29285
	mr	5, 28
	rldic 4, 4, 32, 1
	li 7, 0
	oris 6, 4, 26483
	mr	4, 29
	bl read_one_field
	lis 4, 7001
	addi 3, 30, 144
	ori 4, 4, 22809
	mr	5, 28
	rldic 4, 4, 34, 1
	li 7, 0
	oris 4, 4, 27753
	ori 6, 4, 28263
	mr	4, 29
	bl read_one_field
	lis 4, 28771
	addi 3, 30, 168
	ori 4, 4, 26975
	mr	5, 28
	rldic 26, 4, 32, 1
	li 7, 0
	oris 4, 26, 25205
	ori 6, 4, 29440
	mr	4, 29
	bl read_one_field
	oris 4, 26, 25701
	addi 3, 30, 192
	ori 6, 4, 30208
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	oris 4, 26, 26229
	addi 3, 30, 216
	ori 6, 4, 28160
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	lis 4, 13495
	addi 3, 30, 240
	ori 4, 4, 14905
	mr	5, 28
	rldic 26, 4, 33, 1
	mr	4, 29
	mr	6, 26
	li 7, 0
	bl read_one_field
	addi 3, 30, 264
	ori 6, 26, 1
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	addi 3, 30, 288
	ori 6, 26, 2
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	addi 3, 30, 312
	ori 6, 26, 3
	mr	4, 29
	mr	5, 28
	li 7, 0
	bl read_one_field
	lis 4, 114
	addi 3, 30, 336
	ori 4, 4, 25959
	mr	5, 28
	rldic 26, 4, 40, 1
	mr	4, 29
	mr	6, 26
	mr	7, 27
	bl read_one_field
	lis 4, 25697
	addi 3, 30, 360
	ori 4, 4, 29793
	mr	5, 28
	rldic 25, 4, 32, 1
	mr	4, 29
	mr	6, 26
	mr	7, 25
	bl read_one_field
	ori 24, 26, 1
	addi 3, 30, 384
	mr	4, 29
	mr	5, 28
	mr	6, 24
	mr	7, 27
	bl read_one_field
	addi 3, 30, 408
	mr	4, 29
	mr	5, 28
	mr	6, 24
	mr	7, 25
	bl read_one_field
	ori 26, 26, 2
	addi 3, 30, 432
	mr	4, 29
	mr	5, 28
	mr	6, 26
	mr	7, 27
	bl read_one_field
	addi 3, 30, 456
	mr	4, 29
	mr	5, 28
	mr	6, 26
	mr	7, 25
	addi 1, 1, 96
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	ld 28, -32(1)
	ld 27, -40(1)
	ld 26, -48(1)
	ld 25, -56(1)
	ld 24, -64(1)
	b read_one_field
	#TC_RETURNd8 read_one_field 0
	.long	0
	.quad	0
.Lfunc_end5:
	.size	dump_node, .Lfunc_end5-.Lfunc_begin5

	.p2align	2
	.type	read_one_field,@function
read_one_field:
.Lfunc_begin6:
.Lfunc_gep6:
	addis 2, 12, .TOC.-.Lfunc_gep6@ha
	addi 2, 2, .TOC.-.Lfunc_gep6@l
.Lfunc_lep6:
	.localentry	read_one_field, .Lfunc_lep6-.Lfunc_gep6
	mflr 0
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -80(1)
	mr	30, 3
	li 3, 0
	std 0, 96(1)
	mr	8, 7
	mr	7, 6
	std 3, 48(1)
	mr	6, 5
	mr	5, 4
	std 3, 40(1)
	addi 3, 1, 48
	addi 4, 1, 40
	lis 29, 147
	bl repo_read
	nop
	lwz 4, 3876(29)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 3876(29)
	beq	0, .LBB6_3
	ori 4, 29, 3876
	lwz 5, 12(4)
	cmplwi	5, 0
	bne	0, .LBB6_3
	stw 3, 12(4)
.LBB6_3:
	std 3, 0(30)
	ld 3, 48(1)
	std 3, 8(30)
	ld 3, 40(1)
	std 3, 16(30)
	addi 1, 1, 80
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	blr
	.long	0
	.quad	0
.Lfunc_end6:
	.size	read_one_field, .Lfunc_end6-.Lfunc_begin6

	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc labels_page_22[TC],labels_page_22
.LC1:
	.tc labels_page_07[TC],labels_page_07
.LC2:
	.tc labels_page_09[TC],labels_page_09
.LC3:
	.tc labels_page_12[TC],labels_page_12
.LC4:
	.tc labels_page_19[TC],labels_page_19
.LC5:
	.tc labels_page_11[TC],labels_page_11
.LC6:
	.tc labels_page_14[TC],labels_page_14
.LC7:
	.tc labels_page_21[TC],labels_page_21
.LC8:
	.tc labels_page_08[TC],labels_page_08
.LC9:
	.tc labels_page_20[TC],labels_page_20
.LC10:
	.tc labels_page_16[TC],labels_page_16
.LC11:
	.tc labels_page_00[TC],labels_page_00
.LC12:
	.tc labels_page_06[TC],labels_page_06
.LC13:
	.tc labels_page_03[TC],labels_page_03
.LC14:
	.tc labels_page_18[TC],labels_page_18
.LC15:
	.tc labels_page_02[TC],labels_page_02
.LC16:
	.tc labels_page_10[TC],labels_page_10
.LC17:
	.tc labels_page_17[TC],labels_page_17
.LC18:
	.tc labels_page_05[TC],labels_page_05
.LC19:
	.tc labels_page_13[TC],labels_page_13
.LC20:
	.tc labels_page_15[TC],labels_page_15
.LC21:
	.tc labels_page_01[TC],labels_page_01
.LC22:
	.tc labels_page_04[TC],labels_page_04
.LC23:
	.tc labels_page_23[TC],labels_page_23
