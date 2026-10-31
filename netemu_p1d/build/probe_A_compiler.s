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
	std 0, 224(1)
	lis 5, 147
	std 14, 64(1)
	std 15, 72(1)
	std 16, 80(1)
	std 17, 88(1)
	std 18, 96(1)
	std 19, 104(1)
	std 20, 112(1)
	std 21, 120(1)
	std 22, 128(1)
	ori 22, 5, 3872
	std 23, 136(1)
	std 24, 144(1)
	std 25, 152(1)
	std 26, 160(1)
	std 27, 168(1)
	std 28, 176(1)
	std 29, 184(1)
	std 30, 192(1)
	std 31, 200(1)
	lwz 4, 3872(5)
	andi. 4, 4, 1
	bc 12, 1, .LBB0_36
	std 3, 40(1)
	lis 4, 29817
	li 5, 6745
	lis 6, 98
	lis 7, 50
	lwz 3, 0(22)
	lis 8, 7195
	ori 4, 4, 28773
	ori 3, 3, 1
	rldic 27, 5, 50, 1
	stw 3, 0(22)
	ori 5, 6, 30067
	ori 6, 7, 12987
	ori 7, 8, 56477
	li 21, 0
	std 21, 56(1)
	li 3, -1
	addi 29, 1, 56
	addi 28, 1, 48
	rldic 26, 4, 32, 1
	std 21, 48(1)
	rldic 18, 5, 40, 1
	rldic 17, 6, 41, 1
	stb 3, 35(22)
	rldic 25, 7, 34, 1
	li 15, 0
	stb 3, 32(22)
	stb 3, 33(22)
	stb 3, 34(22)
	stb 3, 36(22)
	stb 3, 37(22)
	stb 3, 38(22)
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
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 20(22)
	beq	0, .LBB0_7
	lwz 4, 24(22)
	cmplwi	4, 0
	bne	0, .LBB0_6
	stw 3, 24(22)
.LBB0_6:
	addi 15, 15, 1
	b .LBB0_2
.LBB0_7:
	ld 30, 56(1)
	cmpldi	30, 5
	bne	0, .LBB0_9
	stb 15, 35(22)
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
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 20(22)
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
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 20(22)
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
	lwz 3, 4(22)
	mr	7, 27
	li 8, 0
	addi 3, 3, 1
	stw 3, 4(22)
	mr	3, 29
	std 16, 56(1)
	std 16, 48(1)
	bl repo_read
	nop
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 20(22)
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
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 20(22)
	beq	0, .LBB0_21
	li 3, 255
	b .LBB0_22
.LBB0_21:
	lwz 3, 60(1)
.LBB0_22:
	cmpldi	19, 5
	bne	0, .LBB0_26
	lwz 4, 8(22)
	addi 4, 4, 1
	stw 4, 8(22)
	lwz 4, 8(22)
	cmplwi	4, 1
	bne	0, .LBB0_30
	stb 15, 32(22)
	stb 14, 33(22)
	stb 3, 34(22)
	std 31, 64(22)
	std 20, 72(22)
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
	lwz 3, 12(22)
	cmplwi	3, 0
	bne	0, .LBB0_15
	li 3, 1
	stw 3, 12(22)
	li 3, 4
	stb 3, 36(22)
	li 3, 2
	stb 14, 37(22)
	stb 3, 38(22)
	std 31, 48(22)
	std 20, 56(22)
	b .LBB0_15
.LBB0_30:
	bc 4, 10, .LBB0_25
.LBB0_31:
	lbz 3, 39(22)
	ori 3, 3, 1
	stb 3, 39(22)
	bc 4, 14, .LBB0_15
.LBB0_32:
	lbz 3, 39(22)
	ori 3, 3, 2
	stb 3, 39(22)
	b .LBB0_15
.LBB0_33:
	lwz 3, 0(22)
	li 4, 0
	li 5, 0
	li 30, 0
	ori 3, 3, 4
	stw 3, 0(22)
	li 3, 9
	bl lv1_open_device
	nop
	lwz 4, 20(22)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 20(22)
	std 3, 80(22)
	stw 3, 40(22)
	bne	0, .LBB0_35
	lwz 3, 0(22)
	ori 3, 3, 8
	stw 3, 0(22)
.LBB0_35:
	std 30, 88(22)
	stw 30, 44(22)
	lwz 3, 0(22)
	ori 3, 3, 2
	stw 3, 0(22)
	ld 3, 40(1)
.LBB0_36:
	lwz 4, 0(22)
	andi. 4, 4, 2
	bne	0, .LBB0_38
	lis 3, 48
	ori 3, 3, 20160
	b .LBB0_83
.LBB0_38:
	clrlwi	3, 3, 30
	cmplwi	3, 3
	beq	0, .LBB0_53
	cmplwi	3, 1
	beq	0, .LBB0_50
	cmplwi	3, 2
	bne	0, .LBB0_56
	lwz 3, 8(22)
	li 4, 0
	cmplwi	3, 0
	li 3, 0
	beq	0, .LBB0_74
	lbz 3, 32(22)
	cmplwi	3, 4
	bne	0, .LBB0_45
	lbz 3, 33(22)
	cmplwi	3, 2
	bne	0, .LBB0_45
	lbz 3, 34(22)
	cmplwi	3, 0
	beq	0, .LBB0_73
.LBB0_45:
	lbz 3, 32(22)
	cmplwi	3, 5
	bne	0, .LBB0_47
	lbz 3, 33(22)
	cmplwi	3, 0
	beq	0, .LBB0_72
.LBB0_47:
	lbz 3, 32(22)
	cmplwi	3, 4
	bne	0, .LBB0_49
	lbz 3, 33(22)
	cmplwi	3, 2
	li 3, 2703
	beq	0, .LBB0_74
.LBB0_49:
	li 3, 3604
	b .LBB0_74
.LBB0_50:
	lwz 3, 0(22)
	andi. 3, 3, 4
	ld 4, 80(22)
	li 3, 528
	beq	0, .LBB0_70
	li 3, -256
	cmplw	4, 3
	blt	0, .LBB0_60
	clrlwi	3, 4, 24
	b .LBB0_70
.LBB0_53:
	lwz 3, 0(22)
	li 4, 0
	andi. 3, 3, 4
	lwz 5, 0(22)
	li 3, 0
	ld 6, 80(22)
	beq	0, .LBB0_63
	addi 4, 6, 17
	cmplwi	4, 17
	bgt	0, .LBB0_62
	ld 6, .LC0@toc(2)
	rldic 4, 4, 2, 30
	add 4, 6, 4
	lwz 4, 96(4)
	b .LBB0_63
.LBB0_56:
	lwz 3, 0(22)
	andi. 3, 3, 4
	ld 4, 80(22)
	li 3, 0
	beq	0, .LBB0_59
	addi 4, 4, 17
	li 3, 704
	cmplwi	4, 17
	bgt	0, .LBB0_59
	ld 3, .LC0@toc(2)
	rldic 4, 4, 1, 31
	add 3, 3, 4
	lhz 3, 16(3)
.LBB0_59:
	ld 4, .LC1@toc(2)
	b .LBB0_71
.LBB0_60:
	cmplwi	4, 255
	bgt	0, .LBB0_69
	ori 3, 4, 256
	b .LBB0_70
.LBB0_62:
	lis 4, 1
	ori 4, 4, 2048
.LBB0_63:
	andi. 5, 5, 16
	ld 5, 88(22)
	beq	0, .LBB0_66
	addi 5, 5, 17
	li 3, 5632
	cmplwi	5, 17
	bgt	0, .LBB0_66
	ld 3, .LC0@toc(2)
	rldic 5, 5, 1, 31
	add 3, 3, 5
	lhz 3, 56(3)
.LBB0_66:
	lwz 5, 24(22)
	li 6, 448
	addi 5, 5, 6
	cmplwi	5, 6
	bgt	0, .LBB0_68
	ld 6, .LC0@toc(2)
	rldic 5, 5, 1, 31
	lhzx 6, 6, 5
.LBB0_68:
	ld 5, .LC2@toc(2)
	add 4, 5, 4
	add 3, 4, 3
	add 3, 3, 6
	b .LBB0_83
.LBB0_69:
	srwi 4, 4, 28
	li 3, 512
	rlwimi 3, 4, 0, 23, 21
.LBB0_70:
	ld 4, .LC3@toc(2)
	rlwinm 3, 3, 6, 0, 25
.LBB0_71:
	add 3, 4, 3
	b .LBB0_83
.LBB0_72:
	li 3, 1802
	b .LBB0_74
.LBB0_73:
	li 3, 901
.LBB0_74:
	lwz 5, 12(22)
	cmplwi	5, 0
	beq	0, .LBB0_82
	lbz 4, 36(22)
	cmplwi	4, 7
	li 4, 40
	bgt	0, .LBB0_77
	lbz 4, 36(22)
	mulli 4, 4, 5
.LBB0_77:
	lbz 5, 37(22)
	li 6, 4
	cmplwi	5, 3
	li 5, 4
	bgt	0, .LBB0_79
	lbz 6, 37(22)
.LBB0_79:
	lbz 7, 38(22)
	cmplwi	7, 3
	bgt	0, .LBB0_81
	lbz 5, 38(22)
.LBB0_81:
	add 4, 6, 4
	lbz 6, 39(22)
	mulli 4, 4, 5
	add 4, 5, 4
	rldimi 6, 4, 2, 0
	addi 4, 6, 1
.LBB0_82:
	ld 5, .LC4@toc(2)
	add 3, 4, 3
	rlwinm 3, 3, 6, 0, 25
	add 3, 5, 3
.LBB0_83:
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

	.type	.L_MergedGlobals,@object
	.section	.rodata,"a",@progbits
	.p2align	3, 0x0
.L_MergedGlobals:
	.short	128
	.short	384
	.short	320
	.short	256
	.short	192
	.short	64
	.short	0
	.space	2
	.short	640
	.short	704
	.short	704
	.short	704
	.short	704
	.short	704
	.short	576
	.short	512
	.short	448
	.short	704
	.short	704
	.short	384
	.short	320
	.short	256
	.short	192
	.short	128
	.short	704
	.short	64
	.space	4
	.short	5120
	.short	5632
	.short	5632
	.short	5632
	.short	5632
	.short	5632
	.short	4608
	.short	4096
	.short	3584
	.short	5632
	.short	5632
	.short	3072
	.short	2560
	.short	2048
	.short	1536
	.short	1024
	.short	5632
	.short	512
	.space	4
	.long	61440
	.long	67584
	.long	67584
	.long	67584
	.long	67584
	.long	67584
	.long	55296
	.long	49152
	.long	43008
	.long	67584
	.long	67584
	.long	36864
	.long	30720
	.long	24576
	.long	18432
	.long	12288
	.long	67584
	.long	6144
	.size	.L_MergedGlobals, 168

.Lswitch.table.s4_menu.3 = .L_MergedGlobals
	.size	.Lswitch.table.s4_menu.3, 14
.Lswitch.table.s4_menu = .L_MergedGlobals+16
	.size	.Lswitch.table.s4_menu, 36
.Lswitch.table.s4_menu.2 = .L_MergedGlobals+56
	.size	.Lswitch.table.s4_menu.2, 36
.Lswitch.table.s4_menu.1 = .L_MergedGlobals+96
	.size	.Lswitch.table.s4_menu.1, 72
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
.LC1:
	.tc labels_page_a[TC],labels_page_a
.LC2:
	.tc labels_page_d[TC],labels_page_d
.LC3:
	.tc labels_page_b[TC],labels_page_b
.LC4:
	.tc labels_page_c[TC],labels_page_c
