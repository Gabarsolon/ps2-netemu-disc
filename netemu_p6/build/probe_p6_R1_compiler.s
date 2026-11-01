	.abiversion 2
	.file	"probe.c"
	.text
	.globl	hddlog_init
	.p2align	2
	.type	hddlog_init,@function
hddlog_init:
.Lfunc_begin0:
.Lfunc_gep0:
	addis 2, 12, .TOC.-.Lfunc_gep0@ha
	addi 2, 2, .TOC.-.Lfunc_gep0@l
.Lfunc_lep0:
	.localentry	hddlog_init, .Lfunc_lep0-.Lfunc_gep0
	mflr 0
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -80(1)
	lis 3, 147
	std 0, 96(1)
	li 30, -1
	ori 26, 3, 3950
	li 3, -54
	ldx 4, 26, 3
	cmpldi	4, 0
	beq	0, .LBB0_3
	ldx 29, 26, 3
	lwz 3, 1644(29)
	cmplwi	3, 0
	beq	0, .LBB0_4
.LBB0_2:
	li 30, 0
.LBB0_3:
	mr	3, 30
	addi 1, 1, 80
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	ld 28, -32(1)
	ld 27, -40(1)
	ld 26, -48(1)
	blr
.LBB0_4:
	bl native_clock
	nop
	std 3, 1696(29)
	li 28, 1
	li 3, 0
	stw 28, 1648(29)
	stw 3, 1652(29)
	bl is_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB0_9
	ld 3, .LC0@toc(2)
	li 27, 0
	addi 4, 3, 402
	li 3, 0
	bl stock_ufs_open
	nop
	mr	28, 3
	cmplwi	28, 7
	ble 0, .LBB0_10
	cmpwi	28, -2
	li 3, 2
	beq	0, .LBB0_8
	li 3, 6
.LBB0_8:
	stb 3, 0(26)
	b .LBB0_3
.LBB0_9:
	stb 28, 0(26)
	lhz 3, -2(26)
	addi 3, 3, 1
	sth 3, -2(26)
	stw 28, 1644(29)
	b .LBB0_3
.LBB0_10:
	li 3, 65
	mtctr 3
	addi 3, 29, -8
	bdz .LBB0_12
.LBB0_11:
	addi 4, 3, 8
	std 27, 8(3)
	mr	3, 4
	bdnz .LBB0_11
.LBB0_12:
	lis 3, 20037
	li 4, 512
	ori 3, 3, 21573
	mr	5, 29
	rldic 3, 3, 32, 1
	li 6, 512
	oris 3, 3, 19797
	ori 3, 3, 19527
	std 3, 0(29)
	lis 3, 1
	stw 3, 8(29)
	stw 4, 12(29)
	stw 3, 16(29)
	li 3, 127
	stw 4, 20(29)
	li 4, 0
	stw 3, 24(29)
	li 3, 1
	stw 3, 28(29)
	ld 3, 1696(29)
	std 3, 32(29)
	li 3, 0
	stw 3, 40(29)
	stw 3, 44(29)
	mr	3, 28
	bl stock_raw_write
	nop
	mr	27, 3
	mr	3, 28
	bl stock_ufs_close
	nop
	cmpldi	27, 512
	bne	0, .LBB0_14
	cmplwi	3, 0
	beq	0, .LBB0_16
.LBB0_14:
	li 3, 6
.LBB0_15:
	stb 3, 0(26)
	b .LBB0_3
.LBB0_16:
	bl is_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB0_19
	bl stock_hdd_cache_flush
	nop
	cmplwi	3, 0
	beq	0, .LBB0_19
	li 3, 7
	b .LBB0_15
.LBB0_19:
	li 3, 1
	stw 3, 1644(29)
	b .LBB0_2
	.long	0
	.quad	0
.Lfunc_end0:
	.size	hddlog_init, .Lfunc_end0-.Lfunc_begin0

	.p2align	2
	.type	is_hdd_log_safe,@function
is_hdd_log_safe:
.Lfunc_begin1:
	lis 3, 577
	lis 6, 578
	ori 3, 3, 51296
	lbz 5, 117(3)
	lbz 4, 104(3)
	xori 5, 5, 1
	ld 6, -14240(6)
	clrlwi	7, 4, 24
	or. 5, 5, 7
	cmpdi 1, 6, 3
	ld 4, 40(3)
	crand 20, 2, 6
	ld 5, 48(3)
	ld 6, 56(3)
	li 3, 0
	bclr 4, 20, 0
	cmpdi	6, 0
	bclr 4, 2, 0
	cmpdi	4, 0
	bclr 4, 2, 0
	cmpdi	5, 0
	bclr 4, 2, 0
	lis 3, 773
	lwz 3, 20864(3)
	cntlzw	3, 3
	srwi 3, 3, 5
	blr
	.long	0
	.quad	0
.Lfunc_end1:
	.size	is_hdd_log_safe, .Lfunc_end1-.Lfunc_begin1

	.globl	hddlog_write
	.p2align	2
	.type	hddlog_write,@function
hddlog_write:
.Lfunc_begin2:
.Lfunc_gep2:
	addis 2, 12, .TOC.-.Lfunc_gep2@ha
	addi 2, 2, .TOC.-.Lfunc_gep2@l
.Lfunc_lep2:
	.localentry	hddlog_write, .Lfunc_lep2-.Lfunc_gep2
	mflr 0
	std 21, -88(1)
	std 22, -80(1)
	std 23, -72(1)
	std 24, -64(1)
	std 25, -56(1)
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -128(1)
	mr	28, 3
	lis 3, 147
	std 0, 144(1)
	ori 22, 3, 3950
	li 3, -54
	mr	23, 4
	ldx 4, 22, 3
	li 30, -1
	cmpldi	4, 0
	beq	0, .LBB2_29
	ldx 29, 22, 3
	lwz 3, 1644(29)
	cmplwi	3, 0
	beq	0, .LBB2_29
	lwz 3, 1648(29)
	cmplwi	3, 128
	blt	0, .LBB2_4
	li 3, 8
	b .LBB2_28
.LBB2_4:
	mr	26, 6
	mr	24, 5
	bl is_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB2_24
	ld 3, .LC0@toc(2)
	li 21, 0
	addi 4, 3, 422
	li 3, 0
	bl stock_ufs_open
	nop
	mr	27, 3
	cmplwi	27, 8
	blt	0, .LBB2_9
	cmpwi	27, -2
	li 3, 2
	beq	0, .LBB2_8
	li 3, 6
.LBB2_8:
	stb 3, 0(22)
	b .LBB2_29
.LBB2_9:
	li 3, 65
	addi 25, 29, 512
	mtctr 3
	li 3, 512
	bdz .LBB2_11
.LBB2_10:
	stdx 21, 29, 3
	addi 3, 3, 8
	bdnz .LBB2_10
.LBB2_11:
	lwz 3, 1652(29)
	li 21, 0
	addi 3, 3, 1
	stw 3, 1652(29)
	lis 3, 19535
	ori 3, 3, 18258
	stw 3, 512(29)
	lwz 3, 1652(29)
	stw 3, 516(29)
	stw 28, 520(29)
	stw 21, 524(29)
	bl native_clock
	nop
	std 3, 528(29)
	cmpldi	26, 0
	std 23, 536(29)
	std 24, 544(29)
	ld 3, 1696(29)
	std 3, 552(29)
	li 3, 0
	beq	0, .LBB2_16
	addi 4, 26, -1
	addi 5, 29, 583
.LBB2_13:
	lbzu 6, 1(4)
	cmpwi	6, 0
	bc 12, 2, .LBB2_16
	cmpldi	3, 438
	bc 12, 1, .LBB2_16
	addi 7, 5, 1
	stb 6, 1(5)
	addi 3, 3, 1
	mr	5, 7
	b .LBB2_13
.LBB2_16:
	add 3, 29, 3
	mr	5, 25
	stb 21, 584(3)
	li 6, 512
	lwz 3, 1648(29)
	sldi 4, 3, 9
	mr	3, 27
	bl stock_raw_write
	nop
	cmpldi	3, 512
	bne	0, .LBB2_26
	lwz 3, 1648(29)
	xoris 4, 28, 17742
	cmplwi	4, 17440
	addi 26, 3, 1
	stw 26, 28(29)
	lwz 3, -6(22)
	addi 3, 3, 1
	stw 3, 44(29)
	bne	0, .LBB2_19
	li 3, 1
	stw 3, 40(29)
	stb 3, 1(22)
.LBB2_19:
	mr	3, 27
	li 4, 0
	mr	5, 29
	li 6, 512
	bl stock_raw_write
	nop
	mr	28, 3
	mr	3, 27
	bl stock_ufs_close
	nop
	cmpldi	28, 512
	bne	0, .LBB2_27
	cmplwi	3, 0
	bne	0, .LBB2_27
	bl is_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB2_24
	bl stock_hdd_cache_flush
	nop
	cmplwi	3, 0
	beq	0, .LBB2_30
	li 3, 7
	b .LBB2_28
.LBB2_24:
	lhz 3, -2(22)
	addi 3, 3, 1
	sth 3, -2(22)
.LBB2_25:
	li 30, 0
	b .LBB2_29
.LBB2_26:
	mr	3, 27
	bl stock_ufs_close
	nop
.LBB2_27:
	li 3, 6
.LBB2_28:
	stb 3, 0(22)
.LBB2_29:
	mr	3, 30
	addi 1, 1, 128
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	ld 28, -32(1)
	ld 27, -40(1)
	ld 26, -48(1)
	ld 25, -56(1)
	ld 24, -64(1)
	ld 23, -72(1)
	ld 22, -80(1)
	ld 21, -88(1)
	blr
.LBB2_30:
	stw 26, 1648(29)
	lwz 3, -6(22)
	addi 3, 3, 1
	stw 3, -6(22)
	b .LBB2_25
	.long	0
	.quad	0
.Lfunc_end2:
	.size	hddlog_write, .Lfunc_end2-.Lfunc_begin2

	.globl	s4_menu
	.p2align	2
	.type	s4_menu,@function
s4_menu:
.Lfunc_begin3:
.Lfunc_gep3:
	addis 2, 12, .TOC.-.Lfunc_gep3@ha
	addi 2, 2, .TOC.-.Lfunc_gep3@l
.Lfunc_lep3:
	.localentry	s4_menu, .Lfunc_lep3-.Lfunc_gep3
	mflr 0
	stdu 1, -432(1)
	cmplwi	3, 8
	std 0, 448(1)
	lis 4, 147
	std 27, 392(1)
	li 27, 0
	std 14, 288(1)
	std 15, 296(1)
	std 16, 304(1)
	std 17, 312(1)
	std 18, 320(1)
	std 19, 328(1)
	std 20, 336(1)
	std 21, 344(1)
	std 22, 352(1)
	std 23, 360(1)
	std 24, 368(1)
	std 25, 376(1)
	std 26, 384(1)
	std 28, 400(1)
	std 29, 408(1)
	std 30, 416(1)
	std 31, 424(1)
	bgt	0, .LBB3_2
	mr	27, 3
.LBB3_2:
	ori 14, 4, 3876
	bl get_arena
	cmpldi	3, 0
	beq	0, .LBB3_18
	mr	29, 3
.LBB3_4:
	bl native_clock
	nop
	ld 4, 60(14)
	lis 5, 1826
	cmpdi	4, 0
	std 3, 60(14)
	sub	3, 3, 4
	ori 4, 5, 31264
	bc 12, 2, .LBB3_7
	cmpld	3, 4
	bc 4, 1, .LBB3_7
	lwz 3, 16(14)
	addi 3, 3, 1
	stw 3, 16(14)
.LBB3_7:
	lwz 3, -4(14)
	addi 16, 1, 160
	andi. 3, 3, 2
	bne	0, .LBB3_59
	lis 3, 1122
	std 27, 112(1)
	ori 3, 3, 30067
	rotldi	26, 3, 40
	bl hddlog_init
	ld 3, .LC0@toc(2)
	std 16, 152(1)
	std 3, 104(1)
	addi 4, 3, 527
	addi 3, 1, 152
	bl append_str
	ld 3, 152(1)
	li 17, 0
	li 4, 1704
	li 5, 1
	mr	6, 16
	stb 17, 0(3)
	lis 3, 16975
	ori 3, 3, 20308
	std 16, 96(1)
	bl hddlog_write
	lis 3, 50
	lis 5, 29285
	lis 4, 29817
	ori 3, 3, 12987
	ori 5, 5, 26473
	ori 4, 4, 28773
	rldic 31, 3, 41, 1
	rldic 3, 5, 32, 1
	li 16, 9
	li 30, 2
	li 18, 0
	addi 25, 1, 144
	addi 24, 1, 136
	addi 23, 1, 128
	addi 22, 1, 120
	li 27, 0
	rldic 21, 4, 32, 1
	oris 20, 3, 28526
	li 28, 0
	li 15, 0
.LBB3_9:
	addi 16, 16, -1
	cmpldi	16, 0
	bc 4, 1, .LBB3_22
	add 19, 27, 31
	mr	3, 25
	std 17, 144(1)
	mr	4, 24
	mr	5, 26
	std 17, 136(1)
	mr	6, 19
	mr	7, 21
	li 8, 0
	bl repo_read
	nop
	cmpldi	3, 0
	beq	0, .LBB3_12
.LBB3_11:
	addi 27, 27, 1
	b .LBB3_9
.LBB3_12:
	ld 3, 144(1)
	addi 28, 28, 1
	cmpldi	3, 0
	beq	0, .LBB3_17
	cmpldi	3, 5
	bne	0, .LBB3_11
	mr	3, 23
	mr	4, 22
	std 17, 128(1)
	mr	5, 26
	mr	6, 19
	std 17, 120(1)
	mr	7, 20
	li 8, 0
	bl repo_read
	nop
	cmpldi	3, 0
	bne	0, .LBB3_16
	ld 3, 128(1)
	stw 3, 1628(29)
.LBB3_16:
	addi 15, 15, 1
	mr	30, 27
	b .LBB3_11
.LBB3_17:
	li 18, 1
	b .LBB3_11
.LBB3_18:
	lwz 3, -4(14)
	andi. 3, 3, 8
	lis 3, 48
	ori 28, 3, 20160
	bne	0, .LBB3_82
	lwz 3, -4(14)
	li 4, 3
	li 5, 0
	li 30, 0
	ori 3, 3, 1
	stw 3, -4(14)
	li 3, 4096
	bl native_alloc
	nop
	mr	29, 3
	bl arena_rw
	cmplwi	3, 0
	beq	0, .LBB3_31
	std 29, 20(14)
	lwz 3, -4(14)
	ori 3, 3, 4
	stw 3, -4(14)
	li 3, 1705
	mtctr 3
	addi 3, 29, -1
	bdz .LBB3_4
.LBB3_21:
	addi 4, 3, 1
	stb 30, 1(3)
	mr	3, 4
	bdz .LBB3_4
	b .LBB3_21
.LBB3_22:
	stw 28, 1632(29)
	li 3, 5
	lis 4, 18258
	addi 25, 1, 152
	rldic 21, 3, 44, 17
	stw 15, 36(14)
	ori 26, 4, 17440
	mr	3, 25
	stw 18, 40(14)
	ld 31, 104(1)
	ld 16, 96(1)
	addi 4, 31, 273
	std 16, 152(1)
	bl append_str
	clrldi	24, 15, 32
	mr	3, 25
	mr	4, 24
	bl format_dec
	addi 4, 31, 25
	mr	3, 25
	bl append_str
	clrldi	23, 18, 32
	mr	3, 25
	mr	4, 23
	bl format_dec
	addi 4, 31, 191
	mr	3, 25
	bl append_str
	ld 3, 152(1)
	li 18, 0
	mr	4, 24
	mr	5, 23
	mr	6, 16
	stb 18, 0(3)
	lis 3, 21315
	ori 3, 3, 16718
	bl hddlog_write
	lis 3, 581
	lis 4, 582
	ori 3, 3, 33832
	ld 25, 16(3)
	ld 24, -31704(4)
	rldicl 4, 25, 32, 12
	rldicl 4, 4, 32, 16
	xor 4, 4, 21
	rldicl 5, 24, 33, 11
	ld 3, 8(3)
	rotldi	5, 5, 31
	xoris 5, 5, 32768
	or. 4, 4, 5
	mcrf 1, 0
	rldicl. 4, 3, 45, 19
	crorc 20, 2, 6
	bc 4, 20, .LBB3_24
	ld 27, .LC0@toc(2)
	li 3, 1
	addi 28, 1, 152
	stw 3, 8(14)
	li 3, -1
	addi 4, 27, 689
	stw 3, 12(14)
	mr	3, 28
	std 16, 152(1)
	bl append_str
	ld 3, 152(1)
	li 23, 0
	mr	4, 25
	mr	5, 24
	mr	6, 16
	stb 23, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 27, 759
	mr	3, 28
	std 16, 152(1)
	bl append_str
	ld 3, 152(1)
	stb 23, 0(3)
	lwz 21, 8(14)
	b .LBB3_58
.LBB3_24:
	std 25, 1672(29)
	addi 4, 31, 627
	std 24, 1680(29)
	std 3, 1688(29)
	addi 3, 1, 152
	std 16, 152(1)
	bl append_str
	ld 3, 152(1)
	mr	4, 25
	mr	5, 24
	mr	6, 16
	stb 18, 0(3)
	mr	3, 26
	bl hddlog_write
	lis 3, 578
	li 22, 0
	ld 3, -14240(3)
	mr	27, 30
	cmpldi	3, 3
	bne	0, .LBB3_29
	lis 3, 577
	li 4, -4096
	ori 3, 3, 51296
	rldicl 4, 4, 20, 16
	ld 22, 16(3)
	and 4, 22, 4
	ld 18, 24(3)
	cmpld	4, 21
	beq	0, .LBB3_27
	li 18, 0
.LBB3_27:
	beq	0, .LBB3_29
	li 22, 0
.LBB3_29:
	addi 23, 1, 152
	addi 4, 31, 483
	std 16, 152(1)
	mr	3, 23
	bl append_str
	ld 3, 152(1)
	li 28, 0
	li 4, 4
	mr	5, 27
	mr	6, 16
	stb 28, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 170
	li 4, 4
	li 6, 0
	li 7, 0
	mr	5, 27
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(14)
	mr	26, 3
	mr	3, 23
	addi 4, 4, 1
	stw 4, 0(14)
	addi 4, 31, 288
	stw 26, 1604(29)
	std 16, 152(1)
	bl append_str
	clrldi	4, 26, 32
	mr	3, 23
	bl format_dec
	ld 3, 152(1)
	mr	4, 26
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	bl hddlog_write
	cmpldi	26, 0
	beq	0, .LBB3_32
	li 3, 2
	li 21, 0
	stw 3, 8(14)
	stw 26, 12(14)
	b .LBB3_54
.LBB3_31:
	lwz 3, -4(14)
	ori 3, 3, 8
	stw 3, -4(14)
	b .LBB3_82
.LBB3_32:
	li 5, 0
	ld 26, .LC0@toc(2)
	lis 3, 20562
	stw 5, 76(1)
	addi 5, 1, 152
	ori 30, 3, 17696
	std 5, 88(1)
	li 5, 16391
	lis 4, 20559
	rotldi	3, 5, 61
	li 6, 0
	std 3, 64(1)
	addi 3, 26, 462
	ori 15, 4, 21332
	std 3, 80(1)
	li 3, 0
	li 20, 0
	stw 3, 72(1)
.LBB3_33:
	subfic 3, 6, 8
	mtctr 3
	addi 3, 6, -2
.LBB3_34:
	bdz .LBB3_50
	addi 4, 3, 2
	addi 5, 3, 3
	stw 5, 1640(29)
	cmpldi	4, 3
	mr	17, 25
	blt	0, .LBB3_39
	cmpldi	4, 5
	mr	17, 22
	blt	0, .LBB3_39
	cmpldi	3, 3
	mr	17, 18
	beq	0, .LBB3_39
	mr	17, 24
.LBB3_39:
	cmpldi	17, 0
	addi 3, 3, 1
	beq	0, .LBB3_34
	cmpldi	20, 0
	mulli 3, 3, 24
	addi 23, 4, 1
	add 19, 26, 3
	std 23, 96(1)
	beq	0, .LBB3_44
	lwz 3, 828(19)
	lwz 4, 76(1)
	cmplw	4, 3
	bne	0, .LBB3_43
	lwz 4, 72(1)
	lbz 3, 826(19)
	clrlwi	4, 4, 24
	cmplw	4, 3
	beq	0, .LBB3_47
.LBB3_43:
	addi 21, 1, 152
	addi 4, 26, 350
	std 16, 152(1)
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 20
	bl format_hex64
	ld 3, 152(1)
	mr	4, 20
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 30
	bl hddlog_write
	li 3, 175
	li 4, 4
	li 7, 0
	mr	5, 27
	mr	6, 20
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	mr	20, 3
	lwz 3, 0(14)
	addi 4, 26, 303
	addi 3, 3, 1
	stw 3, 0(14)
	mr	3, 21
	std 16, 152(1)
	bl append_str
	clrldi	4, 20, 32
	mr	3, 21
	bl format_dec
	ld 3, 152(1)
	mr	4, 20
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 15
	bl hddlog_write
.LBB3_44:
	ld 20, 88(1)
	li 23, 0
	mr	28, 15
	ld 4, 80(1)
	mr	3, 20
	std 16, 152(1)
	bl append_str
	mr	21, 30
	mr	30, 16
	lwz 16, 828(19)
	mr	3, 20
	mr	4, 16
	bl format_hex32
	addi 4, 26, 67
	mr	3, 20
	bl append_str
	lbz 15, 826(19)
	mr	3, 20
	mr	4, 15
	bl format_dec
	ld 3, 152(1)
	mr	4, 16
	mr	5, 15
	mr	6, 30
	stb 23, 0(3)
	mr	3, 21
	mr	23, 26
	mr	26, 21
	bl hddlog_write
	li 3, 174
	li 4, 4
	mr	5, 27
	mr	6, 16
	mr	7, 15
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	mr	21, 3
	lwz 3, 0(14)
	cmpldi	21, 0
	addi 3, 3, 1
	stw 3, 0(14)
	stw 21, 1608(29)
	beq	0, .LBB3_46
	addi 20, 1, 152
	addi 4, 23, 442
	std 30, 152(1)
	mr	3, 20
	bl append_str
	clrldi	4, 21, 32
	mr	3, 20
	bl format_dec
	ld 3, 152(1)
	li 20, 0
	mr	4, 21
	li 5, 0
	mr	6, 30
	stb 20, 0(3)
	mr	3, 28
	mr	15, 28
	bl hddlog_write
	ld 6, 96(1)
	mr	16, 30
	mr	30, 26
	mr	26, 23
	li 28, 0
	b .LBB3_33
.LBB3_46:
	ld 20, 76(14)
	addi 21, 1, 152
	addi 4, 23, 599
	mr	3, 21
	std 20, 1656(29)
	std 30, 152(1)
	bl append_str
	mr	3, 21
	mr	4, 20
	bl format_hex64
	ld 3, 152(1)
	li 4, 0
	mr	5, 20
	mr	6, 30
	stb 4, 0(3)
	mr	3, 28
	std 28, 56(1)
	bl hddlog_write
	b .LBB3_48
.LBB3_47:
	lwz 3, 76(1)
	mr	23, 26
	mr	26, 30
	mr	30, 16
	mr	16, 3
	lwz 3, 72(1)
	std 15, 56(1)
	mr	15, 3
.LBB3_48:
	addi 28, 1, 152
	addi 4, 23, 138
	std 30, 152(1)
	mr	3, 28
	bl append_str
	lbz 21, 824(19)
	mr	3, 28
	mr	4, 21
	bl format_dec
	addi 4, 23, 148
	mr	3, 28
	bl append_str
	mr	3, 28
	mr	4, 17
	bl format_hex64
	addi 4, 23, 81
	mr	3, 28
	std 4, 40(1)
	bl append_str
	lwz 19, 832(19)
	mr	3, 28
	mr	4, 19
	bl format_hex32
	addi 4, 23, 89
	mr	3, 28
	bl append_str
	ld 4, 64(1)
	mr	3, 28
	bl format_hex64
	ld 3, 152(1)
	li 4, 0
	mr	5, 19
	mr	6, 30
	stb 4, 0(3)
	mr	3, 26
	mr	4, 17
	bl hddlog_write
	ld 9, 64(1)
	li 3, 176
	li 4, 4
	mr	5, 27
	mr	6, 17
	std 19, 48(1)
	mr	7, 20
	mr	8, 19
	bl lv1_hcall
	nop
	lwz 4, 0(14)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(14)
	addi 4, 23, 158
	stw 3, 1612(29)
	mr	3, 28
	ld 19, 76(14)
	std 30, 152(1)
	bl append_str
	mr	3, 28
	mr	4, 21
	bl format_dec
	addi 4, 23, 31
	mr	3, 28
	bl append_str
	clrldi	4, 17, 32
	mr	3, 28
	bl format_dec
	addi 4, 23, 204
	mr	3, 28
	bl append_str
	mr	3, 28
	mr	4, 19
	bl format_hex64
	ld 3, 152(1)
	li 4, 0
	mr	5, 19
	mr	6, 30
	ld 28, 56(1)
	stb 4, 0(3)
	mr	3, 28
	mr	4, 17
	bl hddlog_write
	cmpldi	17, 0
	ld 6, 96(1)
	stw 16, 76(1)
	mr	16, 30
	mr	30, 26
	mr	26, 23
	stw 15, 72(1)
	mr	15, 28
	li 28, 0
	bne	0, .LBB3_33
	addi 25, 1, 152
	addi 4, 26, 384
	stw 21, 1636(29)
	mr	3, 25
	std 19, 1664(29)
	std 16, 152(1)
	bl append_str
	mr	3, 25
	mr	4, 20
	bl format_hex64
	ld 4, 40(1)
	mr	3, 25
	bl append_str
	ld 24, 48(1)
	mr	3, 25
	mr	4, 24
	bl format_hex32
	ld 3, 152(1)
	li 28, 0
	mr	4, 20
	mr	5, 24
	mr	6, 16
	stb 28, 0(3)
	mr	3, 30
	bl hddlog_write
	li 3, 177
	li 4, 4
	mr	5, 27
	mr	6, 20
	mr	7, 24
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(14)
	mr	24, 3
	addi 4, 4, 1
	stw 4, 0(14)
	addi 4, 26, 318
	stw 3, 1616(29)
	mr	3, 25
	std 16, 152(1)
	bl append_str
	clrldi	4, 24, 32
	mr	3, 25
	bl format_dec
	ld 3, 152(1)
	mr	4, 24
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 15
	bl hddlog_write
	b .LBB3_51
.LBB3_50:
	li 21, 0
.LBB3_51:
	cmpldi	20, 0
	beq	0, .LBB3_53
	addi 25, 1, 152
	addi 4, 26, 350
	std 16, 152(1)
	mr	3, 25
	bl append_str
	mr	3, 25
	mr	4, 20
	bl format_hex64
	ld 3, 152(1)
	li 28, 0
	mr	4, 20
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 30
	bl hddlog_write
	li 3, 175
	li 4, 4
	li 7, 0
	mr	5, 27
	mr	6, 20
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(14)
	mr	24, 3
	addi 4, 4, 1
	stw 4, 0(14)
	addi 4, 26, 303
	stw 3, 1620(29)
	mr	3, 25
	std 16, 152(1)
	bl append_str
	clrldi	4, 24, 32
	mr	3, 25
	bl format_dec
	ld 3, 152(1)
	mr	4, 24
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 15
	bl hddlog_write
.LBB3_53:
	addi 25, 1, 152
	addi 4, 26, 550
	std 16, 152(1)
	mr	3, 25
	bl append_str
	ld 3, 152(1)
	li 28, 0
	li 4, 4
	mr	5, 27
	mr	6, 16
	stb 28, 0(3)
	mr	3, 30
	bl hddlog_write
	li 3, 171
	li 4, 4
	li 6, 0
	li 7, 0
	mr	5, 27
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(14)
	mr	27, 3
	addi 4, 4, 1
	stw 4, 0(14)
	addi 4, 26, 334
	stw 3, 1624(29)
	mr	3, 25
	std 16, 152(1)
	bl append_str
	clrldi	4, 27, 32
	mr	3, 25
	bl format_dec
	ld 3, 152(1)
	mr	4, 27
	li 5, 0
	mr	6, 16
	stb 28, 0(3)
	mr	3, 15
	bl hddlog_write
.LBB3_54:
	addi 4, 31, 573
	addi 3, 1, 152
	std 16, 152(1)
	bl append_str
	cmplwi	21, 0
	beq	0, .LBB3_56
	addi 27, 1, 152
	addi 4, 31, 74
	mr	3, 27
	bl append_str
	clrldi	4, 21, 32
	mr	3, 27
	bl format_dec
	li 28, 0
	li 27, 0
	b .LBB3_57
.LBB3_56:
	addi 31, 31, 657
	li 27, -17
	li 28, 4
.LBB3_57:
	addi 3, 1, 152
	mr	4, 31
	bl append_str
	stw 28, 8(14)
	li 4, 0
	stw 27, 12(14)
	ld 3, 152(1)
	stb 4, 0(3)
.LBB3_58:
	lwz 5, 0(14)
	lis 3, 17742
	clrldi	4, 21, 32
	ori 3, 3, 17440
	addi 6, 1, 160
	bl hddlog_write
	lwz 3, -4(14)
	ori 3, 3, 2
	stw 3, -4(14)
	ld 27, 112(1)
.LBB3_59:
	cmplwi	27, 6
	rldic 3, 27, 6, 26
	add 3, 29, 3
	addi 28, 3, 1024
	stdx 28, 0, 16
	beq	0, .LBB3_71
	cmplwi	27, 1
	beq	0, .LBB3_75
	cmplwi	27, 2
	beq	0, .LBB3_73
	cmplwi	27, 3
	beq	0, .LBB3_68
	cmplwi	27, 4
	beq	0, .LBB3_70
	cmplwi	27, 5
	beq	0, .LBB3_69
	cmplwi	27, 0
	bne	0, .LBB3_72
	ld 26, .LC0@toc(2)
	addi 3, 1, 160
	addi 4, 26, 37
	bl append_str
	lwz 3, 8(14)
	cmplwi	3, 1
	bne	0, .LBB3_77
	addi 4, 26, 505
	b .LBB3_80
.LBB3_68:
	ld 26, .LC0@toc(2)
	addi 27, 1, 160
	mr	3, 27
	addi 4, 26, 245
	bl append_str
	ld 4, 1680(29)
	mr	3, 27
	bl format_hex64
	addi 4, 26, 15
	mr	3, 27
	bl append_str
	ld 4, 1688(29)
	b .LBB3_74
.LBB3_69:
	ld 26, .LC0@toc(2)
	addi 27, 1, 160
	mr	3, 27
	addi 4, 26, 113
	bl append_str
	lwz 4, 1604(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 121
	mr	3, 27
	bl append_str
	lwz 4, 1608(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 49
	mr	3, 27
	bl append_str
	lwz 4, 1612(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 20
	mr	3, 27
	bl append_str
	lwz 4, 1624(29)
	b .LBB3_76
.LBB3_70:
	ld 26, .LC0@toc(2)
	addi 27, 1, 160
	mr	3, 27
	addi 4, 26, 169
	bl append_str
	ld 4, 1656(29)
	mr	3, 27
	bl format_hex64
	addi 4, 26, 105
	mr	3, 27
	bl append_str
	ld 4, 1664(29)
	b .LBB3_74
.LBB3_71:
	ld 26, .LC0@toc(2)
	addi 27, 1, 160
	mr	3, 27
	addi 4, 26, 180
	bl append_str
	lwz 4, 36(14)
	mr	3, 27
	bl format_dec
	addi 4, 26, 55
	mr	3, 27
	bl append_str
	lwz 4, 40(14)
	mr	3, 27
	bl format_dec
	addi 4, 26, 61
	mr	3, 27
	bl append_str
	lwz 4, 1632(29)
	b .LBB3_76
.LBB3_72:
	ld 3, .LC0@toc(2)
	addi 4, 3, 259
	b .LBB3_80
.LBB3_73:
	ld 3, .LC0@toc(2)
	addi 27, 1, 160
	addi 4, 3, 231
	mr	3, 27
	bl append_str
	ld 4, 1672(29)
.LBB3_74:
	mr	3, 27
	bl format_hex64
	b .LBB3_81
.LBB3_75:
	ld 26, .LC0@toc(2)
	addi 27, 1, 160
	mr	3, 27
	addi 4, 26, 5
	bl append_str
	lwz 4, 1636(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 129
	mr	3, 27
	bl append_str
	lwz 4, 1640(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 10
	mr	3, 27
	bl append_str
	lwz 4, 0(14)
	mr	3, 27
	bl format_dec
	addi 4, 26, 43
	mr	3, 27
	bl append_str
	lwz 4, 68(14)
.LBB3_76:
	mr	3, 27
	bl format_dec
	b .LBB3_81
.LBB3_77:
	lwz 3, 1636(29)
	cmplwi	3, 0
	beq	0, .LBB3_79
	addi 27, 1, 160
	addi 4, 26, 217
	mr	3, 27
	bl append_str
	lwz 4, 1636(29)
	mr	3, 27
	bl format_dec
	addi 4, 26, 97
	b .LBB3_80
.LBB3_79:
	addi 4, 26, 722
.LBB3_80:
	addi 3, 1, 160
	bl append_str
.LBB3_81:
	ldx 3, 0, 16
	li 4, 0
	stb 4, 0(3)
.LBB3_82:
	mr	3, 28
	ld 31, 424(1)
	ld 30, 416(1)
	ld 29, 408(1)
	ld 28, 400(1)
	ld 27, 392(1)
	ld 26, 384(1)
	ld 25, 376(1)
	ld 24, 368(1)
	ld 23, 360(1)
	ld 22, 352(1)
	ld 21, 344(1)
	ld 20, 336(1)
	ld 19, 328(1)
	ld 18, 320(1)
	ld 17, 312(1)
	ld 16, 304(1)
	ld 15, 296(1)
	ld 14, 288(1)
	addi 1, 1, 432
	ld 0, 16(1)
	mtlr 0
	blr
	.long	0
	.quad	0
.Lfunc_end3:
	.size	s4_menu, .Lfunc_end3-.Lfunc_begin3

	.p2align	2
	.type	get_arena,@function
get_arena:
.Lfunc_begin4:
.Lfunc_gep4:
	addis 2, 12, .TOC.-.Lfunc_gep4@ha
	addi 2, 2, .TOC.-.Lfunc_gep4@l
.Lfunc_lep4:
	.localentry	get_arena, .Lfunc_lep4-.Lfunc_gep4
	mflr 0
	std 30, -16(1)
	stdu 1, -48(1)
	std 0, 64(1)
	lis 3, 147
	ld 30, 3896(3)
	mr	3, 30
	bl arena_rw
	cmplwi	3, 0
	li 3, 0
	beq	0, .LBB4_2
	mr	3, 30
.LBB4_2:
	addi 1, 1, 48
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	blr
	.long	0
	.quad	0
.Lfunc_end4:
	.size	get_arena, .Lfunc_end4-.Lfunc_begin4

	.p2align	2
	.type	arena_rw,@function
arena_rw:
.Lfunc_begin5:
	lis 4, 147
	ld 5, 18816(4)
	rldicl 4, 5, 36, 5
	rotldi	4, 4, 28
	xoris 4, 4, 32768
	cmpldi	4, 0
	li 4, 0
	bne	0, .LBB5_4
	lis 6, 581
	ld 6, 26040(6)
	cmpld	6, 5
	bne	0, .LBB5_4
	lis 6, 580
	oris 7, 5, 2
	ld 6, 25992(6)
	clrldi	8, 3, 58
	cmpld 1, 3, 7
	xor 6, 6, 7
	or. 6, 8, 6
	crorc 20, 4, 2
	bc 12, 20, .LBB5_4
	addi 3, 3, 4096
	oris 4, 5, 6
	subc	4, 4, 3
	subfe 3, 3, 3
	addi 4, 3, 1
.LBB5_4:
	clrldi	3, 4, 32
	blr
	.long	0
	.quad	0
.Lfunc_end5:
	.size	arena_rw, .Lfunc_end5-.Lfunc_begin5

	.p2align	2
	.type	append_str,@function
append_str:
.Lfunc_begin6:
	addi 4, 4, -1
.LBB6_1:
	lbzu 5, 1(4)
	cmplwi	5, 0
	beqlr	0
	ld 6, 0(3)
	addi 7, 6, 1
	std 7, 0(3)
	stb 5, 0(6)
	b .LBB6_1
	.long	0
	.quad	0
.Lfunc_end6:
	.size	append_str, .Lfunc_end6-.Lfunc_begin6

	.p2align	2
	.type	format_dec,@function
format_dec:
.Lfunc_begin7:
	cmplwi	4, 0
	beq	0, .LBB7_7
	addi 8, 1, -13
	li 5, 0
	li 6, 10
	mr	7, 8
.LBB7_2:
	cmplwi	4, 0
	beq	0, .LBB7_4
	divwu 9, 4, 6
	addi 5, 5, 1
	mulli 10, 9, 10
	sub	4, 4, 10
	ori 4, 4, 48
	stb 4, 1(8)
	addi 10, 8, 1
	addi 7, 7, 1
	mr	4, 9
	mr	8, 10
	b .LBB7_2
.LBB7_4:
	addi 4, 5, 1
	mtctr 4
	addi 4, 1, -12
	add 5, 4, 5
	li 4, 0
.LBB7_5:
	bdzlr
	ld 6, 0(3)
	addi 4, 4, -1
	lbz 7, -1(5)
	addi 8, 6, 1
	addi 5, 5, -1
	std 8, 0(3)
	stb 7, 0(6)
	b .LBB7_5
.LBB7_7:
	ld 4, 0(3)
	addi 5, 4, 1
	std 5, 0(3)
	li 3, 48
	stb 3, 0(4)
	blr
	.long	0
	.quad	0
.Lfunc_end7:
	.size	format_dec, .Lfunc_end7-.Lfunc_begin7

	.p2align	2
	.type	format_hex64,@function
format_hex64:
.Lfunc_begin8:
.Lfunc_gep8:
	addis 2, 12, .TOC.-.Lfunc_gep8@ha
	addi 2, 2, .TOC.-.Lfunc_gep8@l
.Lfunc_lep8:
	.localentry	format_hex64, .Lfunc_lep8-.Lfunc_gep8
	ld 6, .LC0@toc(2)
	li 5, 17
	mtctr 5
	li 5, 60
.LBB8_1:
	bdzlr
	srd 7, 4, 5
	ld 8, 0(3)
	addi 5, 5, -4
	clrldi	7, 7, 60
	add 7, 6, 7
	lbz 7, 367(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB8_1
	.long	0
	.quad	0
.Lfunc_end8:
	.size	format_hex64, .Lfunc_end8-.Lfunc_begin8

	.p2align	2
	.type	format_hex32,@function
format_hex32:
.Lfunc_begin9:
.Lfunc_gep9:
	addis 2, 12, .TOC.-.Lfunc_gep9@ha
	addi 2, 2, .TOC.-.Lfunc_gep9@l
.Lfunc_lep9:
	.localentry	format_hex32, .Lfunc_lep9-.Lfunc_gep9
	ld 6, .LC0@toc(2)
	li 5, 9
	mtctr 5
	li 5, 28
.LBB9_1:
	bdzlr
	srw 7, 4, 5
	ld 8, 0(3)
	addi 5, 5, -4
	clrlwi	7, 7, 28
	add 7, 6, 7
	lbz 7, 367(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB9_1
	.long	0
	.quad	0
.Lfunc_end9:
	.size	format_hex32, .Lfunc_end9-.Lfunc_begin9

	.type	.L_MergedGlobals,@object
	.section	.rodata,"a",@progbits
	.p2align	3, 0x0
.L_MergedGlobals:
	.asciz	" ok!"
	.asciz	"WIN="
	.asciz	" HC="
	.asciz	" SZ="
	.asciz	" CL="
	.asciz	" hdd="
	.asciz	": rc="
	.asciz	"P6-R1"
	.asciz	" LOG="
	.asciz	" MAP="
	.asciz	" HDD="
	.asciz	" TOT="
	.asciz	" pexp="
	.asciz	"cand #"
	.asciz	" len=0x"
	.asciz	" flg=0x"
	.asciz	" MAP OK"
	.asciz	" BUS=0x"
	.asciz	"RC: OP="
	.asciz	" ALLOC="
	.asciz	" TESTED="
	.asciz	"pre map #"
	.asciz	": lpar=0x"
	.asciz	"post map #"
	.asciz	"DMA RGN=0x"
	.asciz	"SCAN: ROM="
	.asciz	" bus=4 dev=2"
	.asciz	" bus_addr=0x"
	.asciz	" DONE: CAND #"
	.asciz	"CDVD LPAR: 0x"
	.asciz	"CDVD EA:   0x"
	.asciz	"P6-R1 RUNNING"
	.asciz	"scan: rom_cnt="
	.asciz	"post open: rc="
	.asciz	"post free: rc="
	.asciz	"post unmap: rc="
	.asciz	"post close: rc="
	.asciz	"pre free: rgn=0x"
	.asciz	"0123456789abcdef"
	.asciz	"pre unmap: rgn=0x"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"post dma_alloc: rc="
	.asciz	"pre dma_alloc: sz=0x"
	.asciz	"pre open: bus=4 dev=2"
	.asciz	" SANITY REJECT (0 HC)"
	.asciz	"boot: ps2_netemu_p6_r1"
	.asciz	"pre close: bus=4 dev=2"
	.asciz	"finish: ps2_netemu_p6_r1 "
	.asciz	"post dma_alloc: rc=0 rgn=0x"
	.asciz	"grd ok: lpar & ea sanity pass"
	.asciz	"all map candidates failed (-17)"
	.asciz	"grd reject: sanity failed (0 hc)"
	.asciz	" FAIL: ALL CANDIDATES REJECTED (-17)"
	.asciz	"finish: ps2_netemu_p6_r1 failed step=1"
	.space	2
	.byte	1
	.byte	0
	.byte	20
	.byte	0
	.long	1048576
	.long	1048576
	.space	4
	.quad	-2305843009213691904
	.byte	2
	.byte	0
	.byte	16
	.byte	0
	.long	1048576
	.long	524288
	.space	4
	.quad	-2305843009213691904
	.byte	3
	.byte	0
	.byte	12
	.byte	0
	.long	524288
	.long	524288
	.space	4
	.quad	-2305843009213691904
	.byte	4
	.byte	1
	.byte	16
	.byte	0
	.long	524288
	.long	524288
	.space	4
	.quad	-2305843009213691904
	.byte	5
	.byte	1
	.byte	12
	.byte	0
	.long	524288
	.long	524288
	.space	4
	.quad	-2305843009213691904
	.byte	6
	.byte	2
	.byte	16
	.byte	0
	.long	524288
	.long	524288
	.space	4
	.quad	-2305843009213691904
	.byte	7
	.byte	3
	.byte	20
	.byte	0
	.long	1048576
	.long	1048576
	.space	4
	.quad	-2305843009213691904
	.size	.L_MergedGlobals, 968

.L.str.28 = .L_MergedGlobals
	.size	.L.str.28, 5
.L.str.36 = .L_MergedGlobals+5
	.size	.L.str.36, 5
.L.str.38 = .L_MergedGlobals+10
	.size	.L.str.38, 5
.L.str.42 = .L_MergedGlobals+15
	.size	.L.str.42, 5
.L.str.48 = .L_MergedGlobals+20
	.size	.L.str.48, 5
.L.str.2 = .L_MergedGlobals+25
	.size	.L.str.2, 6
.L.str.20 = .L_MergedGlobals+31
	.size	.L.str.20, 6
.L.str.31 = .L_MergedGlobals+37
	.size	.L.str.31, 6
.L.str.39 = .L_MergedGlobals+43
	.size	.L.str.39, 6
.L.str.47 = .L_MergedGlobals+49
	.size	.L.str.47, 6
.L.str.50 = .L_MergedGlobals+55
	.size	.L.str.50, 6
.L.str.51 = .L_MergedGlobals+61
	.size	.L.str.51, 6
.L.str.12 = .L_MergedGlobals+67
	.size	.L.str.12, 7
.L.str.27 = .L_MergedGlobals+74
	.size	.L.str.27, 7
.L.str.17 = .L_MergedGlobals+81
	.size	.L.str.17, 8
.L.str.18 = .L_MergedGlobals+89
	.size	.L.str.18, 8
.L.str.34 = .L_MergedGlobals+97
	.size	.L.str.34, 8
.L.str.44 = .L_MergedGlobals+105
	.size	.L.str.44, 8
.L.str.45 = .L_MergedGlobals+113
	.size	.L.str.45, 8
.L.str.46 = .L_MergedGlobals+121
	.size	.L.str.46, 8
.L.str.37 = .L_MergedGlobals+129
	.size	.L.str.37, 9
.L.str.15 = .L_MergedGlobals+138
	.size	.L.str.15, 10
.L.str.16 = .L_MergedGlobals+148
	.size	.L.str.16, 10
.L.str.19 = .L_MergedGlobals+158
	.size	.L.str.19, 11
.L.str.43 = .L_MergedGlobals+169
	.size	.L.str.43, 11
.L.str.49 = .L_MergedGlobals+180
	.size	.L.str.49, 11
.L.str.3 = .L_MergedGlobals+191
	.size	.L.str.3, 13
.L.str.21 = .L_MergedGlobals+204
	.size	.L.str.21, 13
.L.str.33 = .L_MergedGlobals+217
	.size	.L.str.33, 14
.L.str.40 = .L_MergedGlobals+231
	.size	.L.str.40, 14
.L.str.41 = .L_MergedGlobals+245
	.size	.L.str.41, 14
.L.str.52 = .L_MergedGlobals+259
	.size	.L.str.52, 14
.L.str.1 = .L_MergedGlobals+273
	.size	.L.str.1, 15
.L.str.8 = .L_MergedGlobals+288
	.size	.L.str.8, 15
.L.str.10 = .L_MergedGlobals+303
	.size	.L.str.10, 15
.L.str.23 = .L_MergedGlobals+318
	.size	.L.str.23, 16
.L.str.25 = .L_MergedGlobals+334
	.size	.L.str.25, 16
.L.str.9 = .L_MergedGlobals+350
	.size	.L.str.9, 17
.L__const.format_hex32.hex = .L_MergedGlobals+367
	.size	.L__const.format_hex32.hex, 17
.L.str.22 = .L_MergedGlobals+384
	.size	.L.str.22, 18
hddlog_init.path = .L_MergedGlobals+402
	.size	hddlog_init.path, 20
hddlog_write.path = .L_MergedGlobals+422
	.size	hddlog_write.path, 20
.L.str.13 = .L_MergedGlobals+442
	.size	.L.str.13, 20
.L.str.11 = .L_MergedGlobals+462
	.size	.L.str.11, 21
.L.str.7 = .L_MergedGlobals+483
	.size	.L.str.7, 22
.L.str.32 = .L_MergedGlobals+505
	.size	.L.str.32, 22
.L.str = .L_MergedGlobals+527
	.size	.L.str, 23
.L.str.24 = .L_MergedGlobals+550
	.size	.L.str.24, 23
.L.str.26 = .L_MergedGlobals+573
	.size	.L.str.26, 26
.L.str.14 = .L_MergedGlobals+599
	.size	.L.str.14, 28
.L.str.6 = .L_MergedGlobals+627
	.size	.L.str.6, 30
.L.str.29 = .L_MergedGlobals+657
	.size	.L.str.29, 32
.L.str.4 = .L_MergedGlobals+689
	.size	.L.str.4, 33
.L.str.35 = .L_MergedGlobals+722
	.size	.L.str.35, 37
.L.str.5 = .L_MergedGlobals+759
	.size	.L.str.5, 39
candidates = .L_MergedGlobals+800
	.size	candidates, 168
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
