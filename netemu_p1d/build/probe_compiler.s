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
	mfcr 12
	stw 12, 8(1)
	mflr 0
	stdu 1, -208(1)
	lis 4, 147
	std 0, 224(1)
	std 14, 64(1)
	std 15, 72(1)
	std 16, 80(1)
	std 17, 88(1)
	std 18, 96(1)
	std 19, 104(1)
	std 20, 112(1)
	std 21, 120(1)
	std 22, 128(1)
	ori 22, 4, 3892
	std 23, 136(1)
	std 24, 144(1)
	std 25, 152(1)
	std 26, 160(1)
	std 27, 168(1)
	std 28, 176(1)
	std 29, 184(1)
	std 30, 192(1)
	std 31, 200(1)
	lwz 4, -20(22)
	andi. 4, 4, 1
	bc 12, 1, .LBB0_34
	std 3, 40(1)
	li 5, 6745
	lis 6, 98
	lis 7, 50
	lis 8, 7195
	lwz 3, -20(22)
	rldic 27, 5, 50, 1
	ori 5, 6, 30067
	ori 3, 3, 1
	ori 6, 7, 12987
	stw 3, -20(22)
	lis 3, 29817
	ori 7, 8, 56477
	ori 3, 3, 28773
	li 4, -1
	stb 4, 15(22)
	li 21, 0
	addi 29, 1, 56
	addi 28, 1, 48
	rldic 26, 3, 32, 1
	stb 4, 12(22)
	rldic 18, 5, 40, 1
	rldic 17, 6, 41, 1
	stb 4, 13(22)
	rldic 25, 7, 34, 1
	li 15, 0
	stb 4, 14(22)
	stb 4, 16(22)
	stb 4, 17(22)
	stb 4, 18(22)
.LBB0_2:
	cmpldi	15, 16
	beq	0, .LBB0_33
	or 24, 15, 18
	mr	3, 29
	std 21, 56(1)
	mr	4, 28
	mr	5, 24
	std 21, 48(1)
	mr	6, 26
	li 7, 0
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(22)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(22)
	beq	0, .LBB0_7
	lwz 4, 4(22)
	cmplwi	4, 0
	bne	0, .LBB0_6
	stw 3, 4(22)
.LBB0_6:
	addi 15, 15, 1
	b .LBB0_2
.LBB0_7:
	ld 30, 56(1)
	cmpldi	30, 5
	bne	0, .LBB0_9
	stb 15, 15(22)
.LBB0_9:
	li 14, 0
	mr	3, 29
	std 14, 56(1)
	mr	4, 28
	mr	5, 24
	mr	6, 27
	li 7, 0
	std 14, 48(1)
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(22)
	beq	0, .LBB0_11
	li 31, 0
	b .LBB0_12
.LBB0_11:
	ld 31, 56(1)
.LBB0_12:
	cmpdi 2, 30, 5
	cmpdi 3, 15, 4
	li 30, 17
.LBB0_13:
	addi 30, 30, -1
	cmpldi	30, 0
	bc 4, 1, .LBB0_6
	add 23, 14, 17
	mr	3, 29
	std 21, 56(1)
	mr	4, 28
	mr	5, 24
	std 21, 48(1)
	mr	6, 23
	mr	7, 26
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(22)
	beq	0, .LBB0_16
.LBB0_15:
	addi 14, 14, 1
	b .LBB0_13
.LBB0_16:
	ld 19, 56(1)
	li 16, 0
	mr	4, 28
	mr	5, 24
	mr	6, 23
	lwz 3, -16(22)
	mr	7, 27
	li 8, 0
	addi 3, 3, 1
	stw 3, -16(22)
	mr	3, 29
	std 16, 56(1)
	std 16, 48(1)
	bl repo_read
	nop
	lwz 4, 0(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(22)
	beq	0, .LBB0_18
	li 20, 0
	b .LBB0_19
.LBB0_18:
	ld 20, 56(1)
.LBB0_19:
	mr	3, 29
	mr	4, 28
	std 16, 56(1)
	mr	5, 24
	mr	6, 23
	std 16, 48(1)
	mr	7, 25
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(22)
	beq	0, .LBB0_21
	li 3, 255
	b .LBB0_22
.LBB0_21:
	lwz 3, 60(1)
.LBB0_22:
	cmpldi	19, 5
	bne	0, .LBB0_26
	lwz 4, -12(22)
	addi 4, 4, 1
	stw 4, -12(22)
	lwz 4, -12(22)
	cmplwi	4, 1
	beq	0, .LBB0_30
	bc 12, 10, .LBB0_31
.LBB0_25:
	bc 4, 14, .LBB0_15
	b .LBB0_32
.LBB0_26:
	cmpdi	19, 0
	crand 20, 14, 2
	bc 4, 20, .LBB0_15
	cmpwi	3, 2
	bc 4, 2, .LBB0_15
	lwz 3, -8(22)
	cmplwi	3, 0
	bne	0, .LBB0_15
	li 3, 1
	stw 3, -8(22)
	li 3, 4
	stb 3, 16(22)
	li 3, 2
	stb 14, 17(22)
	stb 3, 18(22)
	std 31, 28(22)
	std 20, 36(22)
	b .LBB0_15
.LBB0_30:
	stb 15, 12(22)
	stb 14, 13(22)
	stb 3, 14(22)
	std 31, 44(22)
	std 20, 52(22)
	bc 4, 10, .LBB0_25
.LBB0_31:
	lbz 3, 19(22)
	ori 3, 3, 1
	stb 3, 19(22)
	bc 4, 14, .LBB0_15
.LBB0_32:
	lbz 3, 19(22)
	ori 3, 3, 2
	stb 3, 19(22)
	b .LBB0_15
.LBB0_33:
	lwz 3, -20(22)
	ori 3, 3, 2
	stw 3, -20(22)
	ld 3, 40(1)
.LBB0_34:
	lwz 4, -20(22)
	andi. 4, 4, 2
	bne	0, .LBB0_36
	lis 3, 48
	ori 3, 3, 20160
	b .LBB0_79
.LBB0_36:
	clrlwi	3, 3, 30
	cmplwi	3, 3
	beq	0, .LBB0_67
	cmplwi	3, 1
	beq	0, .LBB0_47
	cmplwi	3, 2
	bne	0, .LBB0_70
	lwz 3, -8(22)
	cmplwi	3, 0
	beq	0, .LBB0_74
	lbz 3, 16(22)
	cmplwi	3, 7
	li 3, 40
	bgt	0, .LBB0_42
	lbz 3, 16(22)
	mulli 3, 3, 5
.LBB0_42:
	lbz 4, 17(22)
	li 5, 4
	cmplwi	4, 3
	li 4, 4
	bgt	0, .LBB0_44
	lbz 5, 17(22)
.LBB0_44:
	lbz 6, 18(22)
	cmplwi	6, 3
	bgt	0, .LBB0_46
	lbz 4, 18(22)
.LBB0_46:
	add 3, 5, 3
	lbz 5, 19(22)
	mulli 3, 3, 5
	add 3, 4, 3
	ld 4, .LC0@toc(2)
	rldimi 5, 3, 2, 0
	mulli 3, 5, 48
	addi 3, 3, 48
	rlwinm 3, 3, 0, 0, 27
	b .LBB0_78
.LBB0_47:
	lwz 3, -12(22)
	cmplwi	3, 0
	beq	0, .LBB0_73
	lbz 3, 12(22)
	li 4, 15
	cmplwi	3, 15
	li 3, 15
	bgt	0, .LBB0_50
	lbz 4, 12(22)
.LBB0_50:
	lbz 5, 13(22)
	cmplwi	5, 15
	bgt	0, .LBB0_52
	lbz 3, 13(22)
.LBB0_52:
	lbz 5, 14(22)
	cmplwi	5, 2
	li 5, 3
	bgt	0, .LBB0_54
	lbz 5, 14(22)
.LBB0_54:
	ld 6, 44(22)
	cmpld	6, 4
	bne	0, .LBB0_56
	ld 6, 52(22)
	cmpld	6, 3
	li 6, 0
	beq	0, .LBB0_76
.LBB0_56:
	ld 6, 44(22)
	cmpldi	6, 1280
	bne	0, .LBB0_58
	ld 6, 52(22)
	cmpldi	6, 1281
	li 6, 16
	beq	0, .LBB0_76
.LBB0_58:
	ld 6, 44(22)
	cmpldi	6, 256
	bne	0, .LBB0_60
	ld 6, 52(22)
	cmpldi	6, 512
	li 6, 32
	beq	0, .LBB0_76
.LBB0_60:
	ld 6, 44(22)
	cmpldi	6, 4
	bne	0, .LBB0_62
	ld 6, 52(22)
	cmpldi	6, 0
	beq	0, .LBB0_75
.LBB0_62:
	ld 6, 44(22)
	cmpldi	6, 5
	bne	0, .LBB0_64
	ld 6, 52(22)
	cmpldi	6, 2
	li 6, 64
	beq	0, .LBB0_76
.LBB0_64:
	ld 6, 44(22)
	cmpldi	6, 0
	li 6, 96
	bne	0, .LBB0_76
	ld 6, 52(22)
	cmpldi	6, 0
	li 6, 80
	beq	0, .LBB0_76
	li 6, 96
	b .LBB0_76
.LBB0_67:
	lwz 3, -20(22)
	lwz 5, -20(22)
	rlwinm 4, 3, 30, 31, 31
	ld 3, 60(22)
	rlwinm 29, 5, 28, 31, 31
	bl map_rc_idx
	mr	30, 3
	ld 3, 68(22)
	mr	4, 29
	bl map_rc_idx
	lwz 4, 4(22)
	li 5, 7
	addi 4, 4, 6
	cmplwi	4, 6
	bgt	0, .LBB0_69
	ld 5, .LC1@toc(2)
	clrldi	4, 4, 32
	lbzx 5, 5, 4
.LBB0_69:
	mulli 4, 30, 12
	add 3, 3, 4
	ld 4, .LC2@toc(2)
	slwi 3, 3, 3
	or 3, 5, 3
	mulli 3, 3, 48
	b .LBB0_77
.LBB0_70:
	lwz 3, -12(22)
	cmplwi	3, 4
	li 3, 3456
	bgt	0, .LBB0_72
	lwz 3, -12(22)
	mulli 3, 3, 720
	addi 3, 3, 576
	clrldi	3, 3, 32
.LBB0_72:
	ld 4, .LC3@toc(2)
	b .LBB0_78
.LBB0_73:
	ld 3, .LC4@toc(2)
	b .LBB0_79
.LBB0_74:
	ld 3, .LC0@toc(2)
	b .LBB0_79
.LBB0_75:
	li 6, 48
.LBB0_76:
	add 4, 6, 4
	slwi 3, 3, 2
	slwi 4, 4, 6
	add 3, 5, 3
	add 3, 3, 4
	ld 4, .LC4@toc(2)
	mulli 3, 3, 48
	addi 3, 3, 48
.LBB0_77:
	clrldi	3, 3, 32
.LBB0_78:
	add 3, 4, 3
.LBB0_79:
	ld 31, 200(1)
	ld 30, 192(1)
	ld 29, 184(1)
	ld 28, 176(1)
	ld 27, 168(1)
	ld 26, 160(1)
	ld 25, 152(1)
	ld 24, 144(1)
	ld 23, 136(1)
	ld 22, 128(1)
	ld 21, 120(1)
	ld 20, 112(1)
	ld 19, 104(1)
	ld 18, 96(1)
	ld 17, 88(1)
	ld 16, 80(1)
	ld 15, 72(1)
	ld 14, 64(1)
	addi 1, 1, 208
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	mtocrf 16, 12
	blr
	.long	0
	.quad	0
.Lfunc_end0:
	.size	s4_menu, .Lfunc_end0-.Lfunc_begin0

	.p2align	2
	.type	map_rc_idx,@function
map_rc_idx:
.Lfunc_begin1:
.Lfunc_gep1:
	addis 2, 12, .TOC.-.Lfunc_gep1@ha
	addi 2, 2, .TOC.-.Lfunc_gep1@l
.Lfunc_lep1:
	.localentry	map_rc_idx, .Lfunc_lep1-.Lfunc_gep1
	cmplwi	4, 0
	beq	0, .LBB1_3
	mr	4, 3
	addi 3, 3, 17
	cmpldi	3, 17
	li 3, 11
	bgtlr	0
	ld 3, .LC1@toc(2)
	add 3, 3, 4
	lbz 3, 25(3)
	blr
.LBB1_3:
	li 3, 0
	blr
	.long	0
	.quad	0
.Lfunc_end1:
	.size	map_rc_idx, .Lfunc_end1-.Lfunc_begin1

	.type	.L_MergedGlobals,@object
	.section	.rodata,"a",@progbits
	.p2align	2, 0x0
.L_MergedGlobals:
	.asciz	"\002\006\005\004\003\001"
	.space	1
	.ascii	"\n\013\013\013\013\013\t\b\007\013\013\006\005\004\003\002\013\001"
	.size	.L_MergedGlobals, 26

.Lswitch.table.s4_menu = .L_MergedGlobals
	.size	.Lswitch.table.s4_menu, 7
.Lswitch.table.map_rc_idx = .L_MergedGlobals+8
	.size	.Lswitch.table.map_rc_idx, 18
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc labels_page_c[TC],labels_page_c
.LC1:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
.LC2:
	.tc labels_page_d[TC],labels_page_d
.LC3:
	.tc labels_page_a[TC],labels_page_a
.LC4:
	.tc labels_page_b[TC],labels_page_b
