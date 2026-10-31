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
	stdu 1, -224(1)
	lis 4, 147
	std 0, 240(1)
	mr	5, 3
	std 14, 80(1)
	std 15, 88(1)
	std 16, 96(1)
	std 17, 104(1)
	std 18, 112(1)
	std 19, 120(1)
	std 20, 128(1)
	std 21, 136(1)
	ori 21, 4, 3892
	std 22, 144(1)
	std 23, 152(1)
	std 24, 160(1)
	std 25, 168(1)
	std 26, 176(1)
	std 27, 184(1)
	std 28, 192(1)
	std 29, 200(1)
	std 30, 208(1)
	std 31, 216(1)
	lwz 4, -20(21)
	andi. 4, 4, 1
	bc 12, 1, .LBB0_47
	std 5, 32(1)
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
	std 20, 72(1)
	ori 6, 7, 12987
	ori 7, 8, 56477
	std 20, 64(1)
	ori 8, 9, 26473
	rldic 26, 3, 32, 1
	rldic 3, 4, 40, 1
	stb 5, 15(21)
	addi 29, 1, 72
	addi 28, 1, 64
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
	std 20, 72(1)
	or 23, 14, 3
	mr	3, 29
	mr	5, 23
	std 20, 64(1)
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
	ld 22, 72(1)
	cmpldi	22, 5
	bne	0, .LBB0_9
	stb 14, 15(21)
.LBB0_9:
	li 31, 0
	mr	3, 29
	std 31, 72(1)
	mr	4, 28
	mr	5, 23
	mr	6, 27
	li 7, 0
	std 31, 64(1)
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
	ld 30, 72(1)
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
	std 20, 72(1)
	mr	4, 28
	mr	5, 23
	std 20, 64(1)
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
	ld 18, 72(1)
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
	std 17, 72(1)
	std 17, 64(1)
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
	ld 15, 72(1)
.LBB0_21:
	mr	3, 29
	mr	4, 28
	std 17, 72(1)
	mr	5, 23
	mr	6, 22
	std 17, 64(1)
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
	lwz 3, 76(1)
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
	std 20, 72(1)
	std 20, 64(1)
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
	ld 3, 72(1)
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
	li 30, 0
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
	b .LBB0_45
.LBB0_38:
	ld 3, .LC0@toc(2)
	addi 5, 1, 56
	addi 6, 1, 48
	std 30, 56(1)
	lis 4, 16
	std 30, 48(1)
	bl alloc_buffer
	nop
	stw 3, 96(21)
	cmpdi 5, 3, 0
	ld 4, 56(1)
	std 4, 116(21)
	ld 4, 48(1)
	std 4, 108(21)
	cmpdi	4, 0
	ld 5, 56(1)
	cmpdi 1, 5, 0
	bc 4, 22, .LBB0_42
	cror 20, 2, 6
	bc 12, 20, .LBB0_42
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
	ld 29, 60(21)
	std 29, 124(21)
	beq	0, .LBB0_83
	li 4, 3
	b .LBB0_43
.LBB0_42:
	li 4, 2
.LBB0_43:
	stw 4, 8(21)
	stw 3, 4(21)
.LBB0_44:
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
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 92(21)
.LBB0_45:
	ld 5, 32(1)
.LBB0_46:
	lwz 3, -20(21)
	ori 3, 3, 2
	stw 3, -20(21)
.LBB0_47:
	lwz 3, -20(21)
	andi. 3, 3, 2
	bne	0, .LBB0_49
	lis 3, 48
	ori 3, 3, 20160
	b .LBB0_112
.LBB0_49:
	clrlwi	3, 5, 30
	cmplwi	3, 3
	beq	0, .LBB0_60
	cmplwi	3, 1
	beq	0, .LBB0_56
	cmplwi	3, 2
	bne	0, .LBB0_69
	lwz 3, 100(21)
	andi. 3, 3, 1
	bc 12, 1, .LBB0_80
	lwz 3, 100(21)
	andi. 3, 3, 2
	ld 3, .LC1@toc(2)
	bne	0, .LBB0_88
	ld 4, 140(21)
	cmpldi	4, 0
	beq	0, .LBB0_100
	ld 4, 140(21)
	xoris 4, 4, 514
	cmplwi	4, 14848
	bne	0, .LBB0_89
	b .LBB0_85
.LBB0_56:
	lwz 3, 8(21)
	cmplwi	3, 0
	bne	0, .LBB0_58
	lwz 3, 100(21)
	cmplwi	3, 0
	beq	0, .LBB0_91
.LBB0_58:
	lwz 3, 4(21)
	li 4, -256
	cmplw	3, 4
	blt	0, .LBB0_81
	clrlwi	3, 3, 24
	b .LBB0_87
.LBB0_60:
	lwz 3, -12(21)
	li 4, 0
	cmplwi	3, 0
	li 3, 0
	beq	0, .LBB0_103
	lbz 3, 12(21)
	cmplwi	3, 4
	bne	0, .LBB0_64
	lbz 3, 13(21)
	cmplwi	3, 2
	bne	0, .LBB0_64
	lbz 3, 14(21)
	cmplwi	3, 0
	beq	0, .LBB0_102
.LBB0_64:
	lbz 3, 12(21)
	cmplwi	3, 5
	bne	0, .LBB0_66
	lbz 3, 13(21)
	cmplwi	3, 0
	beq	0, .LBB0_92
.LBB0_66:
	lbz 3, 12(21)
	cmplwi	3, 4
	bne	0, .LBB0_68
	lbz 3, 13(21)
	cmplwi	3, 2
	li 3, 2703
	beq	0, .LBB0_103
.LBB0_68:
	li 3, 3604
	b .LBB0_103
.LBB0_69:
	lwz 3, 100(21)
	cmplwi	3, 0
	beq	0, .LBB0_74
	lwz 3, 100(21)
	andi. 3, 3, 1
	ld 3, .LC2@toc(2)
	bc 12, 1, .LBB0_88
	lwz 4, 100(21)
	andi. 4, 4, 2
	bne	0, .LBB0_85
	lwz 4, 100(21)
	andi. 4, 4, 4
	bne	0, .LBB0_89
	lwz 4, 100(21)
	andi. 4, 4, 8
	bne	0, .LBB0_101
.LBB0_74:
	lwz 3, 8(21)
	cmplwi	3, 0
	beq	0, .LBB0_90
	lwz 3, 8(21)
	li 4, 11
	cmplwi	3, 11
	blt	0, .LBB0_77
	li 3, 11
.LBB0_77:
	lwz 5, 4(21)
	addi 5, 5, 17
	cmplwi	5, 17
	bgt	0, .LBB0_79
	ld 4, .LC0@toc(2)
	clrldi	5, 5, 32
	add 4, 4, 5
	lbz 4, 8(4)
.LBB0_79:
	mulli 3, 3, 12
	add 3, 3, 4
	ld 4, .LC2@toc(2)
	slwi 3, 3, 6
	addi 3, 3, -448
	clrldi	3, 3, 32
	add 3, 4, 3
	b .LBB0_112
.LBB0_80:
	ld 3, .LC1@toc(2)
	b .LBB0_112
.LBB0_81:
	cmplwi	3, 255
	bgt	0, .LBB0_86
	ori 3, 3, 256
	b .LBB0_87
.LBB0_83:
	ld 6, 48(1)
	li 3, 16391
	li 4, 4
	rotldi	9, 3, 61
	li 3, 176
	li 5, 2
	mr	7, 29
	lis 8, 8
	li 30, 4
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 32(21)
	ld 4, 60(21)
	std 4, 132(21)
	beq	0, .LBB0_93
	stw 30, 8(21)
	li 4, 4
	li 5, 2
	li 7, 0
	mr	6, 29
	stw 3, 4(21)
	li 3, 175
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 88(21)
	b .LBB0_44
.LBB0_85:
	addi 3, 3, 128
	b .LBB0_112
.LBB0_86:
	srwi 4, 3, 28
	li 3, 512
	rlwimi 3, 4, 0, 23, 21
.LBB0_87:
	ld 4, .LC3@toc(2)
	rlwinm 3, 3, 6, 0, 25
	add 3, 4, 3
.LBB0_88:
	addi 3, 3, 64
	b .LBB0_112
.LBB0_89:
	addi 3, 3, 192
	b .LBB0_112
.LBB0_90:
	ld 3, .LC2@toc(2)
	b .LBB0_112
.LBB0_91:
	ld 3, .LC3@toc(2)
	b .LBB0_112
.LBB0_92:
	li 3, 1802
	b .LBB0_103
.LBB0_93:
	ld 27, 56(1)
	li 4, 0
	li 5, 0
	li 6, 0
	li 7, 0
	ld 28, 48(1)
	mr	3, 27
	li 8, 0
	li 9, 0
	bl setup_atapi_block
	li 3, 248
	li 4, 2
	li 5, 1
	li 7, 64
	mr	6, 28
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 36(21)
	beq	0, .LBB0_113
	li 4, 5
	stw 4, 8(21)
	stw 3, 4(21)
.LBB0_95:
	addi 26, 28, 4096
	li 4, 18
	li 5, 36
	li 6, 1
	mr	3, 27
	li 7, 1
	mr	8, 26
	li 9, 36
	bl setup_atapi_block
	li 3, 248
	li 4, 2
	li 5, 1
	mr	6, 28
	li 7, 64
	mr	8, 26
	li 9, 36
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 40(21)
	beq	0, .LBB0_121
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_98
	li 4, 6
	stw 4, 8(21)
.LBB0_98:
	lwz 4, 4(21)
	cmplwi	4, 0
	bne	0, .LBB0_124
	stw 3, 4(21)
	b .LBB0_124
.LBB0_100:
	ld 4, 148(21)
	cmpldi	4, 0
	beq	0, .LBB0_115
.LBB0_101:
	addi 3, 3, 256
	b .LBB0_112
.LBB0_102:
	li 3, 901
.LBB0_103:
	lwz 5, -8(21)
	cmplwi	5, 0
	beq	0, .LBB0_111
	lbz 4, 16(21)
	cmplwi	4, 7
	li 4, 40
	bgt	0, .LBB0_106
	lbz 4, 16(21)
	mulli 4, 4, 5
.LBB0_106:
	lbz 5, 17(21)
	li 6, 4
	cmplwi	5, 3
	li 5, 4
	bgt	0, .LBB0_108
	lbz 6, 17(21)
.LBB0_108:
	lbz 7, 18(21)
	cmplwi	7, 3
	bgt	0, .LBB0_110
	lbz 5, 18(21)
.LBB0_110:
	add 4, 6, 4
	lbz 6, 19(21)
	mulli 4, 4, 5
	add 4, 5, 4
	rldimi 6, 4, 2, 0
	addi 4, 6, 1
.LBB0_111:
	ld 5, .LC4@toc(2)
	add 3, 4, 3
	rlwinm 3, 3, 6, 0, 25
	add 3, 5, 3
.LBB0_112:
	ld 31, 216(1)
	ld 30, 208(1)
	ld 29, 200(1)
	ld 28, 192(1)
	ld 27, 184(1)
	ld 26, 176(1)
	ld 25, 168(1)
	ld 24, 160(1)
	ld 23, 152(1)
	ld 22, 144(1)
	ld 21, 136(1)
	ld 20, 128(1)
	ld 19, 120(1)
	ld 18, 112(1)
	ld 17, 104(1)
	ld 16, 96(1)
	ld 15, 88(1)
	ld 14, 80(1)
	addi 1, 1, 224
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	mtocrf 16, 12
	blr
.LBB0_113:
	ld 3, 60(21)
	addi 4, 21, 140
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB0_95
	lwz 3, 100(21)
	ori 3, 3, 1
	stw 3, 100(21)
	li 3, 5
	b .LBB0_123
.LBB0_115:
	ld 4, 116(21)
	lbz 5, 4104(4)
	cmplwi	5, 83
	bne	0, .LBB0_120
	lbz 5, 4105(4)
	cmplwi	5, 79
	bne	0, .LBB0_120
	lbz 5, 4106(4)
	cmplwi	5, 78
	bne	0, .LBB0_120
	lbz 4, 4107(4)
	cmplwi	4, 89
	bne	0, .LBB0_120
	addi 3, 3, 320
	b .LBB0_112
.LBB0_120:
	addi 3, 3, 384
	b .LBB0_112
.LBB0_121:
	ld 3, 60(21)
	addi 4, 21, 148
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB0_124
	lwz 3, 100(21)
	ori 3, 3, 2
	stw 3, 100(21)
	li 3, 6
.LBB0_123:
	stw 3, 8(21)
	b .LBB0_45
.LBB0_124:
	li 3, 177
	li 4, 4
	li 5, 2
	lis 7, 8
	mr	6, 29
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 84(21)
	beq	0, .LBB0_127
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_127
	li 4, 9
	stw 4, 8(21)
	stw 3, 4(21)
.LBB0_127:
	li 3, 175
	li 4, 4
	li 5, 2
	li 7, 0
	mr	6, 29
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(21)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(21)
	stw 3, 88(21)
	beq	0, .LBB0_130
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_130
	li 4, 10
	stw 4, 8(21)
	stw 3, 4(21)
.LBB0_130:
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
	ld 5, 32(1)
	beq	0, .LBB0_46
	lwz 4, 8(21)
	cmplwi	4, 0
	bne	0, .LBB0_46
	li 4, 11
	stw 4, 8(21)
	stw 3, 4(21)
	b .LBB0_46
	.long	0
	.quad	0
.Lfunc_end0:
	.size	s4_menu, .Lfunc_end0-.Lfunc_begin0

	.p2align	2
	.type	setup_atapi_block,@function
setup_atapi_block:
.Lfunc_begin1:
	li 10, 9
	addi 11, 3, -8
	mtctr 10
	li 10, 0
	bdz .LBB1_2
.LBB1_1:
	addi 12, 11, 8
	std 10, 8(11)
	mr	11, 12
	bdnz .LBB1_1
.LBB1_2:
	cmplwi	4, 18
	stb 4, 0(3)
	bne	0, .LBB1_4
	stb 5, 4(3)
.LBB1_4:
	li 4, 12
	stw 4, 32(3)
	li 4, 1
	stw 5, 36(3)
	stw 4, 40(3)
	stw 6, 44(3)
	stw 7, 48(3)
	std 8, 56(3)
	stw 9, 64(3)
	blr
	.long	0
	.quad	0
.Lfunc_end1:
	.size	setup_atapi_block, .Lfunc_end1-.Lfunc_begin1

	.p2align	2
	.type	poll_completion,@function
poll_completion:
.Lfunc_begin2:
.Lfunc_gep2:
	addis 2, 12, .TOC.-.Lfunc_gep2@ha
	addi 2, 2, .TOC.-.Lfunc_gep2@l
.Lfunc_lep2:
	.localentry	poll_completion, .Lfunc_lep2-.Lfunc_gep2
	mflr 0
	std 24, -64(1)
	std 25, -56(1)
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -96(1)
	mr	29, 3
	lis 3, 147
	std 0, 112(1)
	mr	30, 4
	ori 26, 3, 3892
	bl native_clock
	nop
	mr	28, 3
	lis 3, 3
	lis 4, 2441
	ori 25, 3, 3393
	ori 24, 4, 26623
.LBB2_1:
	addi 25, 25, -1
	li 27, 1
	cmpldi	25, 0
	bc 4, 1, .LBB2_5
	li 3, 254
	li 4, 2
	li 6, 0
	li 7, 0
	mr	5, 29
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(26)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(26)
	beq	0, .LBB2_4
	bl native_clock
	nop
	sub	3, 3, 28
	cmplw	3, 24
	ble 0, .LBB2_1
	b .LBB2_5
.LBB2_4:
	ld 3, 60(26)
	li 27, 0
	std 3, 0(30)
.LBB2_5:
	mr	3, 27
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
	blr
	.long	0
	.quad	0
.Lfunc_end2:
	.size	poll_completion, .Lfunc_end2-.Lfunc_begin2

	.type	.L_MergedGlobals,@object
	.section	.rodata,"a",@progbits
	.p2align	2, 0x0
.L_MergedGlobals:
	.asciz	"SB_OPT"
	.space	1
	.ascii	"\n\013\013\013\013\013\t\b\007\013\013\006\005\004\003\002\013\001"
	.size	.L_MergedGlobals, 26

str_sb_opt = .L_MergedGlobals
	.size	str_sb_opt, 7
.Lswitch.table.s4_menu = .L_MergedGlobals+8
	.size	.Lswitch.table.s4_menu, 18
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
.LC1:
	.tc labels_page_c[TC],labels_page_c
.LC2:
	.tc labels_page_a[TC],labels_page_a
.LC3:
	.tc labels_page_b[TC],labels_page_b
.LC4:
	.tc labels_page_d[TC],labels_page_d
