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
	ori 21, 4, 3892
	std 22, 128(1)
	std 23, 136(1)
	std 24, 144(1)
	std 25, 152(1)
	std 26, 160(1)
	std 27, 168(1)
	std 28, 176(1)
	std 29, 184(1)
	std 30, 192(1)
	mr	30, 3
	std 31, 200(1)
	lwz 4, -20(21)
	andi. 4, 4, 1
	bc 12, 1, .LBB0_41
	std 30, 32(1)
	li 4, 6745
	lis 6, 98
	lis 7, 50
	lis 8, 7195
	lwz 3, -20(21)
	lis 9, 29285
	rldic 27, 4, 50, 1
	ori 3, 3, 1
	ori 4, 6, 30067
	stw 3, -20(21)
	lis 3, 29817
	li 20, 0
	ori 3, 3, 28773
	li 5, -1
	std 20, 56(1)
	ori 6, 7, 12987
	ori 7, 8, 56477
	std 20, 48(1)
	ori 8, 9, 26473
	rldic 26, 3, 32, 1
	rldic 3, 4, 40, 1
	stb 5, 15(21)
	addi 29, 1, 56
	addi 28, 1, 48
	rldic 16, 6, 41, 1
	stb 5, 12(21)
	rldic 25, 7, 34, 1
	li 14, 0
	stb 5, 13(21)
	stb 5, 14(21)
	stb 5, 16(21)
	std 3, 40(1)
	rldic 3, 8, 32, 1
	oris 24, 3, 28526
	stb 5, 17(21)
	stb 5, 18(21)
	stw 20, 104(21)
.LBB0_2:
	cmpldi	14, 16
	beq	0, .LBB0_36
	ld 3, 40(1)
	mr	4, 28
	mr	6, 26
	li 7, 0
	li 8, 0
	std 20, 56(1)
	or 23, 14, 3
	mr	3, 29
	mr	5, 23
	std 20, 48(1)
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	beq	0, .LBB0_7
	lwz 4, 4(21)
	cmplwi	4, 0
	bne	0, .LBB0_6
	stw 3, 4(21)
.LBB0_6:
	addi 14, 14, 1
	b .LBB0_2
.LBB0_7:
	ld 22, 56(1)
	cmpldi	22, 5
	bne	0, .LBB0_9
	stb 14, 15(21)
.LBB0_9:
	li 31, 0
	mr	3, 29
	std 31, 56(1)
	mr	4, 28
	mr	5, 23
	mr	6, 27
	li 7, 0
	std 31, 48(1)
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(21)
	beq	0, .LBB0_11
	li 30, 0
	b .LBB0_12
.LBB0_11:
	ld 30, 56(1)
.LBB0_12:
	cmpdi 2, 22, 5
	cmpdi 3, 14, 4
	li 19, 17
.LBB0_13:
	addi 19, 19, -1
	cmpldi	19, 0
	bc 4, 1, .LBB0_6
	add 22, 31, 16
	mr	3, 29
	std 20, 56(1)
	mr	4, 28
	mr	5, 23
	std 20, 48(1)
	mr	6, 22
	mr	7, 26
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpdi	31, 2
	crnand 20, 2, 14
	addi 4, 4, 1
	stw 4, 0(21)
	bc 12, 20, .LBB0_16
	stw 3, 20(21)
.LBB0_16:
	cmpldi	3, 0
	beq	0, .LBB0_18
.LBB0_17:
	addi 31, 31, 1
	b .LBB0_13
.LBB0_18:
	ld 18, 56(1)
	li 17, 0
	mr	4, 28
	mr	5, 23
	mr	6, 22
	lwz 3, -16(21)
	mr	7, 27
	li 8, 0
	addi 3, 3, 1
	stw 3, -16(21)
	mr	3, 29
	std 17, 56(1)
	std 17, 48(1)
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(21)
	beq	0, .LBB0_20
	li 15, 0
	b .LBB0_21
.LBB0_20:
	ld 15, 56(1)
.LBB0_21:
	mr	3, 29
	mr	4, 28
	std 17, 56(1)
	mr	5, 23
	mr	6, 22
	std 17, 48(1)
	mr	7, 25
	li 8, 0
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(21)
	beq	0, .LBB0_23
	li 3, 255
	b .LBB0_24
.LBB0_23:
	lwz 3, 60(1)
.LBB0_24:
	cmpldi	18, 5
	bne	0, .LBB0_31
	lwz 4, -12(21)
	addi 4, 4, 1
	stw 4, -12(21)
	lwz 4, -12(21)
	cmplwi	4, 1
	bne	0, .LBB0_27
	stb 14, 12(21)
	mr	4, 28
	mr	5, 23
	mr	6, 22
	mr	7, 24
	stb 31, 13(21)
	mr	8, 27
	stb 3, 14(21)
	mr	3, 29
	std 30, 44(21)
	std 15, 52(21)
	std 20, 56(1)
	std 20, 48(1)
	bl repo_read
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(21)
	beq	0, .LBB0_35
.LBB0_27:
	bc 4, 10, .LBB0_29
.LBB0_28:
	lbz 3, 19(21)
	ori 3, 3, 1
	stb 3, 19(21)
.LBB0_29:
	bc 4, 14, .LBB0_17
	lbz 3, 19(21)
	ori 3, 3, 2
	stb 3, 19(21)
	b .LBB0_17
.LBB0_31:
	cmpdi	18, 0
	crand 20, 14, 2
	bc 4, 20, .LBB0_17
	cmpwi	3, 2
	bc 4, 2, .LBB0_17
	lwz 3, -8(21)
	cmplwi	3, 0
	bne	0, .LBB0_17
	li 3, 1
	stw 3, -8(21)
	li 3, 4
	stb 3, 16(21)
	li 3, 2
	stb 31, 17(21)
	stb 3, 18(21)
	b .LBB0_17
.LBB0_35:
	ld 3, 56(1)
	stw 3, 104(21)
	bc 12, 10, .LBB0_28
	b .LBB0_29
.LBB0_36:
	li 3, 170
	li 4, 4
	li 5, 2
	li 6, 0
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 24(21)
	beq	0, .LBB0_38
	li 4, 1
	stw 4, 8(21)
	stw 3, 4(21)
	ld 30, 32(1)
	b .LBB0_40
.LBB0_38:
	li 3, 174
	li 4, 4
	li 5, 2
	lis 6, 8
	li 7, 12
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 28(21)
	ld 6, 60(21)
	std 6, 124(21)
	ld 30, 32(1)
	beq	0, .LBB0_72
	li 4, 3
	li 5, 2
	stw 4, 8(21)
	li 4, 4
	li 6, 0
	stw 3, 4(21)
	li 3, 171
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 92(21)
.LBB0_40:
	lwz 3, -20(21)
	ori 3, 3, 2
	stw 3, -20(21)
.LBB0_41:
	lwz 3, -20(21)
	andi. 3, 3, 2
	bne	0, .LBB0_43
	lis 3, 48
	ori 3, 3, 20160
	b .LBB0_102
.LBB0_43:
	clrlwi	3, 30, 30
	cmplwi	3, 3
	beq	0, .LBB0_52
	cmplwi	3, 1
	beq	0, .LBB0_48
	cmplwi	3, 2
	bne	0, .LBB0_61
	ld 3, 124(21)
	lwz 4, 28(21)
	cmplwi	4, 0
	beq	0, .LBB0_80
	ld 3, .LC0@toc(2)
	b .LBB0_102
.LBB0_48:
	lwz 3, 8(21)
	cmplwi	3, 0
	bne	0, .LBB0_50
	lwz 3, 100(21)
	cmplwi	3, 0
	beq	0, .LBB0_87
.LBB0_50:
	lwz 3, 4(21)
	li 4, -256
	cmplw	3, 4
	blt	0, .LBB0_78
	clrlwi	3, 3, 24
	b .LBB0_83
.LBB0_52:
	lwz 3, -12(21)
	li 4, 0
	cmplwi	3, 0
	li 3, 0
	beq	0, .LBB0_93
	lbz 3, 12(21)
	cmplwi	3, 4
	bne	0, .LBB0_56
	lbz 3, 13(21)
	cmplwi	3, 2
	bne	0, .LBB0_56
	lbz 3, 14(21)
	cmplwi	3, 0
	beq	0, .LBB0_92
.LBB0_56:
	lbz 3, 12(21)
	cmplwi	3, 5
	bne	0, .LBB0_58
	lbz 3, 13(21)
	cmplwi	3, 0
	beq	0, .LBB0_90
.LBB0_58:
	lbz 3, 12(21)
	cmplwi	3, 4
	bne	0, .LBB0_60
	lbz 3, 13(21)
	cmplwi	3, 2
	li 3, 2703
	beq	0, .LBB0_93
.LBB0_60:
	li 3, 3604
	b .LBB0_93
.LBB0_61:
	lwz 3, 100(21)
	cmplwi	3, 0
	beq	0, .LBB0_66
	lwz 3, 100(21)
	andi. 3, 3, 1
	ld 3, .LC1@toc(2)
	bc 12, 1, .LBB0_84
	lwz 4, 100(21)
	andi. 4, 4, 2
	bne	0, .LBB0_85
	lwz 4, 100(21)
	andi. 4, 4, 4
	bne	0, .LBB0_91
	lwz 4, 100(21)
	andi. 4, 4, 8
	bne	0, .LBB0_103
.LBB0_66:
	lwz 3, 8(21)
	cmplwi	3, 0
	beq	0, .LBB0_86
	lwz 3, 8(21)
	li 4, 11
	cmplwi	3, 11
	blt	0, .LBB0_69
	li 3, 11
.LBB0_69:
	lwz 5, 4(21)
	addi 5, 5, 17
	cmplwi	5, 17
	bgt	0, .LBB0_71
	ld 4, .LC2@toc(2)
	clrldi	5, 5, 32
	lbzx 4, 4, 5
.LBB0_71:
	mulli 3, 3, 12
	add 3, 3, 4
	ld 4, .LC1@toc(2)
	slwi 3, 3, 6
	addi 3, 3, -448
	clrldi	3, 3, 32
	b .LBB0_89
.LBB0_72:
	li 3, 175
	li 4, 4
	li 5, 2
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 88(21)
	beq	0, .LBB0_75
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_75
	li 4, 10
	stw 4, 8(21)
	stw 3, 4(21)
.LBB0_75:
	li 3, 171
	li 4, 4
	li 5, 2
	li 6, 0
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 92(21)
	beq	0, .LBB0_40
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_40
	li 4, 11
	stw 4, 8(21)
	stw 3, 4(21)
	b .LBB0_40
.LBB0_78:
	cmplwi	3, 255
	bgt	0, .LBB0_82
	ori 3, 3, 256
	b .LBB0_83
.LBB0_80:
	rlwinm. 4, 3, 0, 0, 28
	ld 4, .LC0@toc(2)
	beq	0, .LBB0_88
	addi 3, 4, 576
	b .LBB0_102
.LBB0_82:
	srwi 4, 3, 28
	li 3, 512
	rlwimi 3, 4, 0, 23, 21
.LBB0_83:
	ld 4, .LC3@toc(2)
	rlwinm 3, 3, 6, 0, 25
	add 3, 4, 3
.LBB0_84:
	addi 3, 3, 64
	b .LBB0_102
.LBB0_85:
	addi 3, 3, 128
	b .LBB0_102
.LBB0_86:
	ld 3, .LC1@toc(2)
	b .LBB0_102
.LBB0_87:
	ld 3, .LC3@toc(2)
	b .LBB0_102
.LBB0_88:
	sldi 3, 3, 6
	addi 3, 3, 64
	rlwinm 3, 3, 0, 22, 25
.LBB0_89:
	add 3, 4, 3
	b .LBB0_102
.LBB0_90:
	li 3, 1802
	b .LBB0_93
.LBB0_91:
	addi 3, 3, 192
	b .LBB0_102
.LBB0_92:
	li 3, 901
.LBB0_93:
	lwz 5, -8(21)
	cmplwi	5, 0
	beq	0, .LBB0_101
	lbz 4, 16(21)
	cmplwi	4, 7
	li 4, 40
	bgt	0, .LBB0_96
	lbz 4, 16(21)
	mulli 4, 4, 5
.LBB0_96:
	lbz 5, 17(21)
	li 6, 4
	cmplwi	5, 3
	li 5, 4
	bgt	0, .LBB0_98
	lbz 6, 17(21)
.LBB0_98:
	lbz 7, 18(21)
	cmplwi	7, 3
	bgt	0, .LBB0_100
	lbz 5, 18(21)
.LBB0_100:
	add 4, 6, 4
	lbz 6, 19(21)
	mulli 4, 4, 5
	add 4, 5, 4
	rldimi 6, 4, 2, 0
	addi 4, 6, 1
.LBB0_101:
	ld 5, .LC4@toc(2)
	add 3, 4, 3
	rlwinm 3, 3, 6, 0, 25
	add 3, 5, 3
.LBB0_102:
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
.LBB0_103:
	addi 3, 3, 256
	b .LBB0_102
	.long	0
	.quad	0
.Lfunc_end0:
	.size	s4_menu, .Lfunc_end0-.Lfunc_begin0

	.type	.Lswitch.table.s4_menu,@object
	.section	.rodata,"a",@progbits
	.p2align	2, 0x0
.Lswitch.table.s4_menu:
	.ascii	"\n\013\013\013\013\013\t\b\007\013\013\006\005\004\003\002\013\001"
	.size	.Lswitch.table.s4_menu, 18

	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc labels_page_c[TC],labels_page_c
.LC1:
	.tc labels_page_a[TC],labels_page_a
.LC2:
	.tc .Lswitch.table.s4_menu[TC],.Lswitch.table.s4_menu
.LC3:
	.tc labels_page_b[TC],labels_page_b
.LC4:
	.tc labels_page_d[TC],labels_page_d
