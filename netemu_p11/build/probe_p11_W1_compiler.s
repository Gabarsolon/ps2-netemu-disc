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
	lwz 3, 1668(29)
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
	std 3, 1784(29)
	li 28, 1
	li 3, 0
	stw 28, 1672(29)
	stw 3, 1676(29)
	bl is_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB0_9
	ld 3, .LC0@toc(2)
	li 27, 0
	addi 4, 3, 854
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
	stw 28, 1668(29)
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
	ld 3, 1784(29)
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
	stw 3, 1668(29)
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
	lwz 3, 1668(29)
	cmplwi	3, 0
	beq	0, .LBB2_29
	lwz 3, 1672(29)
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
	addi 4, 3, 874
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
	lwz 3, 1676(29)
	li 21, 0
	addi 3, 3, 1
	stw 3, 1676(29)
	lis 3, 19535
	ori 3, 3, 18258
	stw 3, 512(29)
	lwz 3, 1676(29)
	stw 3, 516(29)
	stw 28, 520(29)
	stw 21, 524(29)
	bl native_clock
	nop
	std 3, 528(29)
	cmpldi	26, 0
	std 23, 536(29)
	std 24, 544(29)
	ld 3, 1784(29)
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
	lwz 3, 1672(29)
	sldi 4, 3, 9
	mr	3, 27
	bl stock_raw_write
	nop
	cmpldi	3, 512
	bne	0, .LBB2_26
	lwz 3, 1672(29)
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
	stw 26, 1672(29)
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
	mfcr 12
	stw 12, 8(1)
	mflr 0
	stdu 1, -608(1)
	cmplwi	3, 8
	std 0, 624(1)
	lis 4, 147
	std 27, 568(1)
	li 27, 0
	std 14, 464(1)
	std 15, 472(1)
	std 16, 480(1)
	std 17, 488(1)
	std 18, 496(1)
	std 19, 504(1)
	std 20, 512(1)
	std 21, 520(1)
	std 22, 528(1)
	std 23, 536(1)
	std 24, 544(1)
	std 25, 552(1)
	std 26, 560(1)
	std 28, 576(1)
	std 29, 584(1)
	std 30, 592(1)
	std 31, 600(1)
	bgt	0, .LBB3_2
	mr	27, 3
.LBB3_2:
	ori 16, 4, 3876
	bl get_arena
	cmpldi	3, 0
	beq	0, .LBB3_18
	mr	14, 3
.LBB3_4:
	bl native_clock
	nop
	ld 4, 60(16)
	lis 5, 1826
	cmpdi	4, 0
	std 3, 60(16)
	sub	3, 3, 4
	ori 4, 5, 31264
	bc 12, 2, .LBB3_7
	cmpld	3, 4
	bc 4, 1, .LBB3_7
	lwz 3, 16(16)
	addi 3, 3, 1
	stw 3, 16(16)
.LBB3_7:
	lwz 3, -4(16)
	addi 29, 1, 208
	andi. 3, 3, 2
	bne	0, .LBB3_38
	lis 3, 1122
	std 14, 152(1)
	ori 3, 3, 30067
	rotldi	26, 3, 40
	std 27, 144(1)
	bl hddlog_init
	ld 3, .LC0@toc(2)
	std 29, 200(1)
	mr	30, 3
	addi 4, 3, 1088
	addi 3, 1, 200
	bl append_str
	ld 3, 200(1)
	li 17, 0
	li 4, 2112
	li 5, 1
	mr	6, 29
	stb 17, 0(3)
	lis 3, 16975
	ori 3, 3, 20308
	bl hddlog_write
	li 3, 2
	lis 5, 29285
	std 3, 160(1)
	lis 3, 50
	lis 4, 29817
	ori 3, 3, 12987
	ori 5, 5, 26473
	ori 4, 4, 28773
	rldic 28, 3, 41, 1
	rldic 3, 5, 32, 1
	li 14, 9
	li 18, 0
	addi 25, 1, 192
	addi 24, 1, 184
	addi 23, 1, 176
	addi 22, 1, 168
	li 27, 0
	rldic 21, 4, 32, 1
	oris 20, 3, 28526
	li 15, 0
	li 31, 0
.LBB3_9:
	addi 14, 14, -1
	cmpldi	14, 0
	bc 4, 1, .LBB3_22
	add 19, 27, 28
	mr	3, 25
	std 17, 192(1)
	mr	4, 24
	mr	5, 26
	std 17, 184(1)
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
	ld 3, 192(1)
	addi 15, 15, 1
	cmpldi	3, 0
	beq	0, .LBB3_17
	cmpldi	3, 5
	bne	0, .LBB3_11
	mr	3, 23
	mr	4, 22
	std 17, 176(1)
	mr	5, 26
	mr	6, 19
	std 17, 168(1)
	mr	7, 20
	li 8, 0
	bl repo_read
	nop
	cmpldi	3, 0
	bne	0, .LBB3_16
	ld 3, 176(1)
	ld 4, 152(1)
	stw 3, 1660(4)
.LBB3_16:
	addi 31, 31, 1
	std 27, 160(1)
	b .LBB3_11
.LBB3_17:
	li 18, 1
	b .LBB3_11
.LBB3_18:
	lwz 3, -4(16)
	andi. 3, 3, 8
	lis 3, 48
	ori 28, 3, 20160
	bne	0, .LBB3_71
	lwz 3, -4(16)
	li 4, 3
	li 5, 0
	li 29, 0
	ori 3, 3, 1
	stw 3, -4(16)
	li 3, 4096
	bl native_alloc
	nop
	mr	14, 3
	bl arena_rw
	cmplwi	3, 0
	beq	0, .LBB3_26
	std 14, 20(16)
	lwz 3, -4(16)
	ori 3, 3, 4
	stw 3, -4(16)
	li 3, 2113
	mtctr 3
	addi 3, 14, -1
	bdz .LBB3_4
.LBB3_21:
	addi 4, 3, 1
	stb 29, 1(3)
	mr	3, 4
	bdz .LBB3_4
	b .LBB3_21
.LBB3_22:
	ld 14, 152(1)
	lis 3, 18258
	addi 26, 1, 200
	ori 19, 3, 17440
	addi 4, 30, 662
	stw 15, 1664(14)
	mr	3, 26
	mr	15, 30
	stw 31, 36(16)
	stw 18, 40(16)
	std 29, 200(1)
	bl append_str
	clrldi	25, 31, 32
	mr	3, 26
	mr	4, 25
	bl format_dec
	addi 4, 30, 49
	mr	3, 26
	bl append_str
	clrldi	24, 18, 32
	mr	3, 26
	mr	4, 24
	bl format_dec
	addi 4, 30, 498
	mr	3, 26
	bl append_str
	ld 3, 200(1)
	li 22, 0
	mr	4, 25
	mr	5, 24
	mr	6, 29
	stb 22, 0(3)
	lis 3, 21315
	ori 3, 3, 16718
	bl hddlog_write
	lis 3, 581
	lis 4, 582
	ori 3, 3, 33832
	li 5, 5
	ld 24, 16(3)
	rldic 5, 5, 44, 17
	ld 23, -31704(4)
	rldicl 4, 24, 32, 12
	rldicl 4, 4, 32, 16
	xor 4, 4, 5
	rldicl 5, 23, 33, 11
	ld 3, 8(3)
	rotldi	5, 5, 31
	xoris 5, 5, 32768
	or. 4, 4, 5
	mcrf 1, 0
	rldicl. 4, 3, 45, 19
	crorc 20, 2, 6
	bc 4, 20, .LBB3_24
	li 3, 1
	addi 27, 1, 200
	stw 3, 8(16)
	li 3, -1
	addi 4, 15, 1312
	stw 3, 12(16)
	mr	3, 27
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	mr	4, 24
	mr	5, 23
	mr	6, 29
	stb 22, 0(3)
	mr	3, 19
	bl hddlog_write
	addi 4, 15, 1449
	mr	3, 27
	std 29, 200(1)
	bl append_str
	b .LBB3_37
.LBB3_24:
	addi 26, 1, 200
	std 24, 1760(14)
	addi 4, 15, 1219
	std 23, 1768(14)
	std 3, 1776(14)
	mr	3, 26
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	mr	4, 24
	mr	5, 23
	mr	6, 29
	stb 22, 0(3)
	mr	3, 19
	bl hddlog_write
	addi 4, 15, 998
	mr	3, 26
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	li 4, 4
	mr	6, 29
	ld 27, 160(1)
	stb 22, 0(3)
	lis 3, 20562
	mr	5, 27
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
	lwz 4, 0(16)
	mr	25, 3
	mr	3, 26
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 677
	stw 25, 1604(14)
	std 29, 200(1)
	bl append_str
	clrldi	4, 25, 32
	mr	3, 26
	bl format_dec
	ld 3, 200(1)
	mr	4, 25
	li 5, 0
	mr	6, 29
	stb 22, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	bl hddlog_write
	cmpldi	25, 0
	beq	0, .LBB3_27
	li 3, 2
	stw 3, 8(16)
	stw 25, 12(16)
	b .LBB3_34
.LBB3_26:
	lwz 3, -4(16)
	ori 3, 3, 8
	stw 3, -4(16)
	b .LBB3_71
.LBB3_27:
	lis 3, 20562
	lis 4, 20559
	std 29, 200(1)
	ori 25, 3, 17696
	ori 26, 4, 21332
	addi 4, 15, 1378
	addi 3, 1, 200
	bl append_str
	ld 3, 200(1)
	li 17, 0
	lis 4, 16
	li 5, 20
	mr	6, 29
	stb 17, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 174
	li 4, 4
	lis 6, 16
	li 7, 20
	mr	5, 27
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	mr	22, 3
	lwz 3, 0(16)
	cmpldi	22, 0
	addi 3, 3, 1
	stw 3, 0(16)
	stw 22, 1608(14)
	beq	0, .LBB3_29
	addi 24, 1, 200
	addi 4, 15, 894
	std 29, 200(1)
	mr	3, 24
	bl append_str
	clrldi	4, 22, 32
	mr	3, 24
	bl format_dec
	ld 3, 200(1)
	mr	4, 22
	li 5, 0
	mr	6, 29
	stb 17, 0(3)
	mr	3, 26
	bl hddlog_write
	li 3, 3
	stw 3, 8(16)
	stw 22, 12(16)
	b .LBB3_32
.LBB3_29:
	ld 22, 76(16)
	addi 21, 1, 200
	addi 4, 15, 1191
	mr	3, 21
	std 22, 1744(14)
	std 29, 200(1)
	bl append_str
	mr	3, 21
	mr	4, 22
	bl format_hex64
	ld 3, 200(1)
	li 4, 0
	mr	5, 22
	mr	6, 29
	stb 17, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 15, 785
	mr	3, 21
	std 29, 200(1)
	bl append_str
	mr	3, 21
	mr	4, 24
	bl format_hex64
	addi 4, 15, 217
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 22
	bl format_hex64
	ld 3, 200(1)
	mr	4, 24
	mr	5, 22
	mr	6, 29
	stb 17, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 16391
	li 4, 4
	rotldi	9, 3, 61
	li 3, 176
	mr	5, 27
	mr	6, 24
	mr	7, 22
	lis 8, 16
	li 28, 4
	bl lv1_hcall
	nop
	lwz 4, 0(16)
	mr	20, 3
	mr	3, 21
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 550
	stw 20, 1612(14)
	ld 18, 76(16)
	std 18, 1752(14)
	std 29, 200(1)
	bl append_str
	clrldi	4, 20, 32
	mr	3, 21
	bl format_dec
	addi 4, 15, 511
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 18
	bl format_hex64
	ld 3, 200(1)
	mr	4, 20
	mr	5, 18
	mr	6, 29
	stb 17, 0(3)
	mr	3, 26
	bl hddlog_write
	cmpldi	20, 0
	beq	0, .LBB3_72
	stw 28, 8(16)
	stw 20, 12(16)
.LBB3_31:
	addi 24, 1, 200
	addi 4, 15, 802
	std 29, 200(1)
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	ld 3, 200(1)
	li 28, 0
	mr	4, 22
	li 5, 0
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 175
	li 4, 4
	li 7, 0
	mr	5, 27
	mr	6, 22
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(16)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 692
	stw 3, 1620(14)
	mr	3, 24
	std 29, 200(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 200(1)
	mr	4, 23
	li 5, 0
	mr	6, 29
	stb 28, 0(3)
	mr	3, 26
	bl hddlog_write
.LBB3_32:
	addi 24, 1, 200
	addi 4, 15, 1042
	std 29, 200(1)
	mr	3, 24
	bl append_str
	ld 3, 200(1)
	li 28, 0
	li 4, 4
	mr	5, 27
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
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
	lwz 4, 0(16)
	mr	27, 3
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 753
	stw 3, 1624(14)
	mr	3, 24
	std 29, 200(1)
	bl append_str
	clrldi	4, 27, 32
	mr	3, 24
	bl format_dec
	ld 3, 200(1)
	mr	4, 27
	li 5, 0
	stb 28, 0(3)
	mr	3, 26
.LBB3_33:
	mr	6, 29
	bl hddlog_write
.LBB3_34:
	addi 4, 15, 1164
	addi 3, 1, 200
	std 29, 200(1)
	bl append_str
	lwz 3, 8(16)
	cmplwi	3, 0
	beq	0, .LBB3_36
	addi 28, 1, 200
	addi 4, 15, 537
	mr	3, 28
	bl append_str
	lwz 4, 8(16)
	mr	3, 28
	bl format_dec
	b .LBB3_37
.LBB3_36:
	addi 4, 15, 620
	addi 3, 1, 200
	bl append_str
	li 3, 0
	stw 3, 12(16)
.LBB3_37:
	ld 3, 200(1)
	li 4, 0
	addi 6, 1, 208
	stb 4, 0(3)
	lis 3, 17742
	ori 3, 3, 17440
	ld 27, 144(1)
	lwz 4, 8(16)
	lwz 5, 0(16)
	bl hddlog_write
	lwz 3, -4(16)
	ori 3, 3, 2
	stw 3, -4(16)
.LBB3_38:
	cmplwi	27, 7
	rldic 3, 27, 6, 26
	add 3, 14, 3
	addi 28, 3, 1024
	stdx 28, 0, 29
	beq	0, .LBB3_57
	cmplwi	27, 1
	beq	0, .LBB3_51
	cmplwi	27, 2
	beq	0, .LBB3_55
	cmplwi	27, 3
	beq	0, .LBB3_54
	cmplwi	27, 4
	beq	0, .LBB3_48
	cmplwi	27, 5
	beq	0, .LBB3_50
	cmplwi	27, 6
	beq	0, .LBB3_49
	cmplwi	27, 0
	bne	0, .LBB3_53
	ld 27, .LC0@toc(2)
	addi 29, 1, 208
	mr	3, 29
	addi 4, 27, 634
	bl append_str
	lbz 3, 2072(14)
	cmpldi	3, 6
	bgt	0, .LBB3_66
	sldi 3, 3, 3
	add 3, 27, 3
	ld 4, 1624(3)
	b .LBB3_67
.LBB3_48:
	ld 30, .LC0@toc(2)
	mr	3, 29
	addi 4, 30, 20
	bl append_str
	lwz 4, 0(16)
	mr	3, 29
	bl format_dec
	addi 4, 30, 127
	mr	3, 29
	bl append_str
	lwz 4, 68(16)
	mr	3, 29
	bl format_dec
	addi 4, 30, 203
	mr	3, 29
	bl append_str
	lhz 4, 72(16)
	mr	3, 29
	bl format_dec
	addi 4, 30, 329
	mr	3, 29
	bl append_str
	lwz 4, 4(16)
	b .LBB3_68
.LBB3_49:
	ld 3, .LC0@toc(2)
	addi 4, 3, 648
	mr	3, 29
	bl append_str
	ld 4, 1760(14)
	b .LBB3_58
.LBB3_50:
	ld 27, .LC0@toc(2)
	mr	3, 29
	addi 4, 27, 486
	bl append_str
	lwz 4, 1720(14)
	mr	3, 29
	bl format_dec
	addi 4, 27, 210
	mr	3, 29
	bl append_str
	lwz 4, 1724(14)
	mr	3, 29
	bl format_dec
	addi 4, 27, 337
	mr	3, 29
	bl append_str
	lwz 4, 1728(14)
	b .LBB3_56
.LBB3_51:
	ld 27, .LC0@toc(2)
	addi 3, 1, 208
	addi 4, 27, 707
	bl append_str
	lbz 3, 1736(14)
	cmpldi	3, 3
	bgt	0, .LBB3_59
	sldi 3, 3, 3
	add 3, 27, 3
	ld 4, 1280(3)
	b .LBB3_60
.LBB3_53:
	ld 3, .LC0@toc(2)
	addi 4, 3, 722
	mr	3, 29
	bl append_str
	b .LBB3_69
.LBB3_54:
	ld 27, .LC0@toc(2)
	mr	3, 29
	addi 4, 27, 440
	bl append_str
	lwa 4, 2008(14)
	mr	3, 29
	bl format_s32
	addi 4, 27, 121
	mr	3, 29
	bl append_str
	lwa 4, 2012(14)
	mr	3, 29
	bl format_s32
	addi 4, 27, 12
	mr	3, 29
	bl append_str
	lwa 4, 2084(14)
	mr	3, 29
	bl format_s32
	addi 4, 27, 16
	mr	3, 29
	bl append_str
	lwa 4, 2092(14)
	mr	3, 29
	bl format_s32
	b .LBB3_69
.LBB3_55:
	ld 27, .LC0@toc(2)
	mr	3, 29
	addi 4, 27, 474
	bl append_str
	lwz 4, 2096(14)
	mr	3, 29
	bl format_dec
	addi 4, 27, 321
	mr	3, 29
	bl append_str
	lwz 4, 2100(14)
	mr	3, 29
	bl format_dec
	addi 4, 27, 44
	mr	3, 29
	bl append_str
	lwz 4, 2088(14)
.LBB3_56:
	mr	3, 29
	bl format_dec
	b .LBB3_69
.LBB3_57:
	ld 27, .LC0@toc(2)
	mr	3, 29
	addi 4, 27, 451
	bl append_str
	ld 4, 1744(14)
	mr	3, 29
	bl format_hex64
	addi 4, 27, 345
	mr	3, 29
	bl append_str
	ld 4, 1752(14)
.LBB3_58:
	mr	3, 29
	bl format_hex64
	b .LBB3_69
.LBB3_59:
	addi 4, 27, 115
.LBB3_60:
	addi 29, 1, 208
	mr	3, 29
	bl append_str
	lbz 3, 1736(14)
	cmplwi	3, 2
	bne	0, .LBB3_69
	addi 4, 27, 196
	mr	3, 29
	bl append_str
	ldx 4, 0, 29
	li 3, 6
	addi 5, 14, 1974
	mtctr 3
	addi 4, 4, -1
.LBB3_62:
	addi 3, 4, 1
	bdz .LBB3_70
	lbz 6, 1(5)
	addi 5, 5, 1
	addi 7, 6, -32
	clrlwi	7, 7, 24
	cmplwi	7, 95
	blt	0, .LBB3_65
	li 6, 46
.LBB3_65:
	stb 6, 1(4)
	mr	4, 3
	b .LBB3_62
.LBB3_66:
	addi 4, 27, 24
.LBB3_67:
	mr	3, 29
	bl append_str
	addi 4, 27, 182
	mr	3, 29
	bl append_str
	lhz 4, 2074(14)
	mr	3, 29
	bl format_hex32
	addi 4, 27, 189
	mr	3, 29
	bl append_str
	lbz 4, 2076(14)
.LBB3_68:
	mr	3, 29
	bl format_hex32
.LBB3_69:
	ldx 3, 0, 29
.LBB3_70:
	li 4, 0
	stb 4, 0(3)
.LBB3_71:
	mr	3, 28
	ld 31, 600(1)
	ld 30, 592(1)
	ld 29, 584(1)
	ld 28, 576(1)
	ld 27, 568(1)
	ld 26, 560(1)
	ld 25, 552(1)
	ld 24, 544(1)
	ld 23, 536(1)
	ld 22, 528(1)
	ld 21, 520(1)
	ld 20, 512(1)
	ld 19, 504(1)
	ld 18, 496(1)
	ld 17, 488(1)
	ld 16, 480(1)
	ld 15, 472(1)
	ld 14, 464(1)
	addi 1, 1, 608
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	mtocrf 16, 12
	blr
.LBB3_72:
	li 4, 0
	li 5, 0
	li 6, 0
	li 7, 0
	mr	3, 23
	li 8, 0
	li 28, 0
	bl setup_atapi_block
	addi 21, 1, 200
	addi 4, 15, 914
	std 29, 200(1)
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 24
	bl format_hex64
	ld 3, 200(1)
	mr	4, 24
	li 5, 0
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 248
	li 5, 1
	li 7, 64
	mr	4, 27
	mr	6, 24
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	mr	17, 3
	lwz 3, 0(16)
	cmpldi	17, 0
	addi 3, 3, 1
	stw 3, 0(16)
	stw 17, 1628(14)
	beq	0, .LBB3_77
	lwz 3, 8(16)
	cmplwi	3, 0
	bne	0, .LBB3_75
	li 3, 5
	stw 3, 8(16)
.LBB3_75:
	lwz 3, 12(16)
	cmplwi	3, 0
	bne	0, .LBB3_79
	stw 17, 12(16)
	b .LBB3_79
.LBB3_77:
	ld 4, 76(16)
	addi 5, 14, 1792
	addi 6, 14, 1680
	addi 7, 14, 1856
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_79
	lwz 3, 4(16)
	addi 4, 15, 1488
	ori 3, 3, 1
	stw 3, 4(16)
	li 3, 5
	stw 3, 8(16)
	addi 3, 1, 200
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	li 4, 0
	stb 4, 0(3)
	lwz 4, 1680(14)
	ld 5, 1856(14)
	b .LBB3_93
.LBB3_79:
	mr	30, 14
	addi 14, 1, 200
	std 29, 200(1)
	addi 4, 15, 564
	mr	3, 14
	ori 21, 23, 4096
	ori 20, 24, 4096
	bl append_str
	clrldi	4, 17, 32
	mr	3, 14
	bl format_dec
	addi 4, 15, 389
	mr	3, 14
	std 4, 136(1)
	bl append_str
	ld 4, 1792(30)
	mr	3, 14
	bl format_hex64
	addi 4, 15, 225
	mr	3, 14
	std 4, 128(1)
	bl append_str
	lwz 4, 1680(30)
	mr	3, 14
	bl format_dec
	addi 4, 15, 233
	mr	3, 14
	bl append_str
	ld 4, 1856(30)
	mr	3, 14
	bl format_hex64
	ld 3, 200(1)
	li 28, 0
	mr	4, 17
	mr	6, 29
	stb 28, 0(3)
	mr	3, 26
	ld 5, 1792(30)
	bl hddlog_write
	li 4, 18
	li 5, 36
	mr	3, 23
	li 6, 1
	li 7, 1
	mr	8, 20
	bl setup_atapi_block
	mr	3, 21
	li 4, 36
	li 5, 0
	bl prefill_buffer
	addi 4, 15, 935
	mr	3, 14
	std 29, 200(1)
	bl append_str
	mr	3, 14
	mr	4, 24
	bl format_hex64
	addi 18, 15, 524
	mr	3, 14
	mr	4, 18
	bl append_str
	mr	3, 14
	mr	4, 20
	bl format_hex64
	ld 3, 200(1)
	mr	4, 24
	mr	5, 20
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 27
	mr	6, 24
	li 7, 64
	mr	8, 20
	li 9, 36
	bl lv1_hcall
	nop
	mr	14, 3
	lwz 3, 0(16)
	cmpldi	14, 0
	addi 3, 3, 1
	stw 3, 0(16)
	stw 14, 1632(30)
	beq	0, .LBB3_89
	lwz 3, 8(16)
	cmplwi	3, 0
	bne	0, .LBB3_82
	li 3, 6
	stw 3, 8(16)
.LBB3_82:
	lwz 3, 12(16)
	cmplwi	3, 0
	bne	0, .LBB3_84
	stw 14, 12(16)
.LBB3_84:
	addi 31, 1, 200
	addi 4, 15, 578
	std 29, 200(1)
	mr	3, 31
	bl append_str
	clrldi	4, 14, 32
	mr	3, 31
	bl format_dec
	ld 4, 136(1)
	mr	3, 31
	bl append_str
	ld 30, 152(1)
	mr	3, 31
	ld 4, 1800(30)
	bl format_hex64
	addi 4, 15, 241
	mr	3, 31
	bl append_str
	addi 4, 21, 8
	mr	3, 31
	li 5, 16
	bl format_ascii
	mr	3, 31
	mr	4, 15
	bl append_str
	ld 3, 200(1)
	li 28, 0
	mr	4, 14
	mr	6, 29
	mr	14, 30
	stb 28, 0(3)
	mr	3, 26
	ld 5, 1800(30)
	bl hddlog_write
	li 4, 37
	li 5, 8
	mr	3, 23
	li 6, 1
	li 7, 1
	mr	8, 20
	bl setup_atapi_block
	mr	3, 21
	li 4, 8
	li 5, 0
	bl prefill_buffer
	addi 4, 15, 956
	mr	3, 31
	std 29, 200(1)
	bl append_str
	mr	3, 31
	mr	4, 24
	bl format_hex64
	mr	3, 31
	mr	4, 18
	bl append_str
	mr	3, 31
	mr	4, 20
	bl format_hex64
	ld 3, 200(1)
	mr	4, 24
	mr	5, 20
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 27
	mr	6, 24
	li 7, 64
	mr	8, 20
	li 9, 8
	bl lv1_hcall
	nop
	mr	18, 3
	lwz 3, 0(16)
	cmpldi	18, 0
	addi 3, 3, 1
	stw 3, 0(16)
	stw 18, 1636(30)
	beq	0, .LBB3_91
	lwz 3, 8(16)
	cmplwi	3, 0
	bne	0, .LBB3_87
	li 3, 7
	stw 3, 8(16)
.LBB3_87:
	lwz 3, 12(16)
	cmplwi	3, 0
	bne	0, .LBB3_97
	stw 18, 12(16)
	b .LBB3_97
.LBB3_89:
	ld 4, 76(16)
	addi 5, 30, 1800
	addi 6, 30, 1684
	addi 7, 30, 1864
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_94
	lwz 3, 4(16)
	addi 4, 15, 1531
	ori 3, 3, 2
	stw 3, 4(16)
	li 3, 6
	stw 3, 8(16)
	addi 3, 1, 200
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	li 4, 0
	mr	6, 29
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 1684(30)
	ld 5, 1864(30)
	bl hddlog_write
	mr	14, 30
	b .LBB3_34
.LBB3_91:
	ld 4, 76(16)
	addi 5, 14, 1808
	addi 6, 14, 1688
	addi 7, 14, 1872
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_96
	lwz 3, 4(16)
	addi 4, 15, 1574
	ori 3, 3, 4
	stw 3, 4(16)
	li 3, 7
	stw 3, 8(16)
	addi 3, 1, 200
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	li 4, 0
	stb 4, 0(3)
	lwz 4, 1688(14)
	ld 5, 1872(14)
.LBB3_93:
	lis 3, 21581
	ori 3, 3, 20256
	b .LBB3_33
.LBB3_94:
	li 3, 37
	addi 4, 30, 1919
	mtctr 3
	li 3, 0
	bdz .LBB3_84
.LBB3_95:
	lbzx 5, 21, 3
	addi 6, 4, 1
	addi 3, 3, 1
	stb 5, 1(4)
	mr	4, 6
	bdz .LBB3_84
	b .LBB3_95
.LBB3_96:
	lbz 3, 0(21)
	lbz 4, 1(21)
	lbz 5, 2(21)
	lbz 6, 3(21)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1712(14)
	lbz 3, 4(21)
	lbz 4, 5(21)
	lbz 5, 6(21)
	lbz 6, 7(21)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1716(14)
.LBB3_97:
	cmpdi 3, 17, 0
	addi 17, 1, 200
	std 29, 200(1)
	addi 4, 15, 592
	mr	3, 17
	cmpdi 2, 18, 0
	bl append_str
	clrldi	4, 18, 32
	mr	3, 17
	bl format_dec
	ld 4, 136(1)
	mr	3, 17
	bl append_str
	ld 4, 1808(14)
	mr	3, 17
	bl format_hex64
	addi 4, 15, 249
	mr	3, 17
	bl append_str
	lwz 4, 1712(14)
	mr	3, 17
	bl format_hex32
	addi 4, 15, 55
	mr	3, 17
	bl append_str
	lwz 4, 1716(14)
	mr	3, 17
	bl format_dec
	ld 3, 200(1)
	li 4, 0
	mr	6, 29
	stb 4, 0(3)
	mr	3, 26
	mr	4, 18
	ld 5, 1808(14)
	bl hddlog_write
	addi 5, 14, 2008
	addi 6, 14, 2032
	addi 7, 15, 2
	li 3, 2
	li 4, 3
	bl query_vuart_param
	addi 5, 14, 2012
	addi 6, 14, 2040
	addi 7, 15, 8
	li 3, 10
	li 4, 3
	bl query_vuart_param
	addi 5, 14, 2016
	addi 6, 14, 2048
	lwa 17, 2012(14)
	addi 7, 15, 133
	li 3, 10
	li 4, 0
	bl query_vuart_param
	bc 4, 14, .LBB3_99
	ld 3, 1792(14)
	cmpldi	3, 0
	beq	0, .LBB3_101
.LBB3_99:
	li 3, 0
	bc 4, 10, .LBB3_102
.LBB3_100:
	ld 4, 1808(14)
	cmpldi	4, 0
	bne	0, .LBB3_102
	b .LBB3_103
.LBB3_101:
	li 3, 1
	bc 12, 10, .LBB3_100
.LBB3_102:
	li 3, 0
.LBB3_103:
	lwz 4, 1716(14)
	xori 4, 4, 2048
	or 4, 17, 4
	cmpwi	4, 0
	bc 4, 2, .LBB3_120
	cmpwi	3, 0
	bc 12, 2, .LBB3_120
	addi 3, 21, 2048
	ori 17, 24, 6144
	bl format_auth_request
	addi 19, 1, 200
	addi 4, 15, 1345
	std 29, 200(1)
	mr	3, 19
	bl append_str
	ld 3, 200(1)
	li 28, 0
	li 4, 10
	li 5, 112
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 163
	li 4, 10
	li 6, 112
	li 7, 0
	mr	5, 17
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(16)
	mr	18, 3
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 977
	ld 17, 76(16)
	stw 3, 2084(14)
	mr	3, 19
	stw 17, 2088(14)
	std 29, 200(1)
	bl append_str
	extsw 4, 18
	mr	3, 19
	bl format_s32
	addi 4, 15, 257
	mr	3, 19
	bl append_str
	clrldi	4, 17, 32
	mr	3, 19
	bl format_dec
	ld 3, 200(1)
	mr	4, 18
	mr	5, 17
	mr	6, 29
	stb 28, 0(3)
	mr	3, 26
	bl hddlog_write
	cmpdi	18, 0
	bc 4, 2, .LBB3_121
	cmpdi	17, 0
	bc 12, 2, .LBB3_121
	addi 3, 21, 2304
	li 4, 112
	li 5, 0
	bl prefill_buffer
	addi 4, 15, 1413
	addi 3, 1, 200
	std 29, 200(1)
	bl append_str
	ld 3, 200(1)
	li 4, 10
	li 5, 112
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	bl native_clock
	nop
	lis 4, 2435
	mr	19, 3
	ori 28, 24, 6400
	li 18, 0
	li 3, 1
	ori 27, 4, 19840
.LBB3_108:
	subfic 4, 18, 112
	clrldi	5, 18, 32
	mr	17, 3
	or 5, 5, 28
	clrldi	6, 4, 32
	li 3, 162
	li 4, 10
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(16)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(16)
	stw 3, 2092(14)
	bne	0, .LBB3_112
	ld 3, 76(16)
	cmpldi	3, 0
	beq	0, .LBB3_111
	add 18, 18, 3
	cmplwi	18, 111
	bgt	0, .LBB3_112
.LBB3_111:
	bl native_clock
	nop
	sub	3, 3, 19
	cmpld	3, 27
	addi 3, 17, 1
	blt	0, .LBB3_108
.LBB3_112:
	bl native_clock
	nop
	cmplwi	18, 4
	sub	3, 3, 19
	stw 18, 2096(14)
	stw 17, 2100(14)
	std 3, 2104(14)
	blt	0, .LBB3_116
	lbz 3, 2304(21)
	cmplwi	18, 36
	lbz 4, 2305(21)
	lbz 5, 2306(21)
	lbz 6, 2307(21)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 2080(14)
	blt	0, .LBB3_116
	lbz 3, 2338(21)
	cmplwi	18, 57
	lbz 4, 2339(21)
	rlwimi 4, 3, 8, 0, 23
	sth 4, 2074(14)
	blt	0, .LBB3_116
	lbz 3, 2360(21)
	stb 3, 2076(14)
.LBB3_116:
	cmplwi	18, 0
	ld 27, 160(1)
	beq	0, .LBB3_122
	cmplwi	18, 112
	bne	0, .LBB3_123
	lhz 3, 2074(14)
	cmplwi	3, 0
	beq	0, .LBB3_136
.LBB3_119:
	li 3, 2
	b .LBB3_124
.LBB3_120:
	li 3, 5
	addi 6, 15, 1137
	stb 3, 2072(14)
	li 3, 1
	mr	5, 17
	stb 3, 2073(14)
	mr	3, 19
	lwz 4, 1716(14)
	b .LBB3_128
.LBB3_121:
	li 3, 6
	stb 3, 2072(14)
	b .LBB3_129
.LBB3_122:
	li 3, 3
	b .LBB3_124
.LBB3_123:
	li 3, 4
.LBB3_124:
	stb 3, 2072(14)
	addi 3, 21, 2368
	li 4, 48
	li 5, 0
	li 28, 0
	bl prefill_buffer
	addi 19, 1, 200
	addi 4, 15, 1020
	std 29, 200(1)
	mr	3, 19
	bl append_str
	clrldi	4, 18, 32
	mr	3, 19
	bl format_dec
	ld 4, 128(1)
	mr	3, 19
	bl append_str
	clrldi	4, 17, 32
	mr	3, 19
	bl format_dec
	addi 4, 15, 353
	mr	3, 19
	bl append_str
	lhz 4, 2074(14)
	mr	3, 19
	bl format_hex32
	addi 4, 15, 265
	mr	3, 19
	bl append_str
	lbz 4, 2076(14)
	mr	3, 19
	bl format_hex32
	addi 4, 15, 61
	mr	3, 19
	bl append_str
	lbz 3, 2072(14)
	cmpldi	3, 6
	bgt	0, .LBB3_126
	sldi 3, 3, 3
	add 3, 15, 3
	ld 4, 1624(3)
	b .LBB3_127
.LBB3_126:
	addi 4, 15, 24
.LBB3_127:
	addi 3, 1, 200
	bl append_str
	ld 3, 200(1)
	addi 6, 1, 208
	stb 28, 0(3)
	mr	3, 26
	lhz 4, 2074(14)
	lbz 5, 2076(14)
.LBB3_128:
	bl hddlog_write
.LBB3_129:
	addi 3, 14, 1640
	addi 4, 14, 1816
	std 14, 64(1)
	addi 5, 14, 1692
	addi 6, 14, 1880
	std 6, 96(1)
	addi 7, 14, 1720
	addi 8, 14, 1736
	std 8, 112(1)
	addi 10, 15, 140
	li 6, 1
	li 8, 8
	li 9, 8
	std 7, 104(1)
	li 7, 1
	std 5, 88(1)
	li 5, 2048
	std 4, 80(1)
	li 4, 16
	std 3, 72(1)
	mr	3, 27
	std 20, 56(1)
	std 21, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_34
	li 3, 33
	addi 4, 14, 1973
	mtctr 3
	li 3, 0
	bdz .LBB3_132
.LBB3_131:
	lbzx 5, 21, 3
	addi 6, 4, 1
	addi 3, 3, 1
	stb 5, 1(4)
	mr	4, 6
	bdnz .LBB3_131
.LBB3_132:
	addi 3, 14, 1644
	addi 4, 14, 1824
	std 14, 64(1)
	addi 5, 14, 1696
	addi 6, 14, 1888
	std 6, 96(1)
	addi 7, 14, 1724
	addi 8, 14, 1737
	std 8, 112(1)
	addi 10, 15, 67
	li 6, 1
	li 8, 9
	li 9, 16
	std 7, 104(1)
	li 7, 1
	std 5, 88(1)
	li 5, 2048
	std 4, 80(1)
	li 4, 0
	std 3, 72(1)
	mr	3, 27
	std 20, 56(1)
	std 21, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_34
	addi 3, 14, 1648
	addi 4, 14, 1832
	std 14, 64(1)
	addi 5, 14, 1700
	addi 6, 14, 1896
	std 6, 96(1)
	addi 7, 14, 1728
	addi 8, 14, 1738
	std 8, 112(1)
	addi 10, 15, 147
	li 6, 1
	li 8, 10
	li 9, 32
	std 7, 104(1)
	li 7, 1
	std 5, 88(1)
	li 5, 2048
	std 4, 80(1)
	li 4, 17
	std 3, 72(1)
	mr	3, 27
	std 20, 56(1)
	std 21, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_34
	addi 3, 14, 1840
	addi 4, 14, 1704
	std 14, 64(1)
	addi 5, 14, 1904
	addi 6, 14, 1732
	std 6, 104(1)
	addi 7, 14, 1739
	addi 11, 14, 1652
	std 7, 112(1)
	addi 10, 15, 154
	li 6, 2048
	li 7, 3
	li 8, 11
	std 5, 96(1)
	li 5, 1
	li 9, 64
	std 4, 88(1)
	li 4, 16
	std 3, 80(1)
	mr	3, 27
	std 20, 56(1)
	std 21, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	std 11, 72(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_34
	addi 24, 1, 200
	addi 4, 15, 836
	std 29, 200(1)
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	addi 4, 15, 606
	mr	3, 24
	bl append_str
	ld 3, 200(1)
	li 28, 0
	mr	4, 22
	lis 5, 16
	mr	6, 29
	stb 28, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 177
	li 4, 4
	lis 7, 16
	mr	5, 27
	mr	6, 22
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(16)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(16)
	addi 4, 15, 737
	stw 3, 1616(14)
	mr	3, 24
	std 29, 200(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 200(1)
	mr	4, 23
	li 5, 0
	mr	6, 29
	stb 28, 0(3)
	mr	3, 26
	bl hddlog_write
	b .LBB3_31
.LBB3_136:
	lbz 3, 2076(14)
	cmplwi	3, 0
	li 3, 1
	beq	0, .LBB3_119
	b .LBB3_124
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
	li 5, 16
	b format_hex_n
	#TC_RETURNd8 format_hex_n 0
	.long	0
	.quad	0
.Lfunc_end8:
	.size	format_hex64, .Lfunc_end8-.Lfunc_begin8

	.p2align	2
	.type	setup_atapi_block,@function
setup_atapi_block:
.Lfunc_begin9:
.Lfunc_gep9:
	addis 2, 12, .TOC.-.Lfunc_gep9@ha
	addi 2, 2, .TOC.-.Lfunc_gep9@l
.Lfunc_lep9:
	.localentry	setup_atapi_block, .Lfunc_lep9-.Lfunc_gep9
	mflr 0
	std 25, -56(1)
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -96(1)
	mr	26, 5
	mr	25, 4
	std 0, 112(1)
	li 4, 64
	li 5, 0
	mr	30, 8
	mr	29, 7
	mr	28, 6
	mr	27, 3
	bl prefill_buffer
	cmplwi	25, 18
	stb 25, 0(27)
	beq	0, .LBB9_2
	cmplwi	25, 3
	bne	0, .LBB9_3
.LBB9_2:
	stb 26, 4(27)
.LBB9_3:
	li 3, 12
	stw 3, 32(27)
	li 3, 1
	stw 26, 36(27)
	stw 3, 40(27)
	stw 28, 44(27)
	stw 29, 48(27)
	std 30, 56(27)
	addi 1, 1, 96
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	ld 28, -32(1)
	ld 27, -40(1)
	ld 26, -48(1)
	ld 25, -56(1)
	blr
	.long	0
	.quad	0
.Lfunc_end9:
	.size	setup_atapi_block, .Lfunc_end9-.Lfunc_begin9

	.p2align	2
	.type	poll_completion,@function
poll_completion:
.Lfunc_begin10:
.Lfunc_gep10:
	addis 2, 12, .TOC.-.Lfunc_gep10@ha
	addi 2, 2, .TOC.-.Lfunc_gep10@l
.Lfunc_lep10:
	.localentry	poll_completion, .Lfunc_lep10-.Lfunc_gep10
	mflr 0
	std 20, -96(1)
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
	mr	25, 3
	lis 3, 147
	std 0, 144(1)
	mr	30, 7
	mr	28, 6
	mr	27, 5
	mr	26, 4
	ori 23, 3, 3876
	bl native_clock
	nop
	mr	29, 3
	lis 3, 3
	lis 4, 2441
	ori 21, 3, 3393
	li 22, 0
	ori 20, 4, 26623
.LBB10_1:
	addi 21, 21, -1
	li 24, 1
	cmpldi	21, 0
	bc 4, 1, .LBB10_6
	li 3, 254
	li 6, 0
	li 7, 0
	mr	4, 25
	mr	5, 26
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(23)
	cmpldi	3, 0
	addi 3, 4, 1
	stw 3, 0(23)
	beq	0, .LBB10_5
	bl native_clock
	nop
	sub	3, 3, 29
	cmpld	3, 20
	bgt	0, .LBB10_6
	addi 22, 22, 1
	b .LBB10_1
.LBB10_5:
	ld 3, 76(23)
	li 24, 0
	std 3, 0(27)
	addi 3, 22, 1
	stw 3, 0(28)
.LBB10_6:
	bl native_clock
	nop
	mr	4, 3
	mr	3, 24
	sub	4, 4, 29
	std 4, 0(30)
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
	ld 20, -96(1)
	blr
	.long	0
	.quad	0
.Lfunc_end10:
	.size	poll_completion, .Lfunc_end10-.Lfunc_begin10

	.p2align	2
	.type	prefill_buffer,@function
prefill_buffer:
.Lfunc_begin11:
	addi 4, 4, 1
	addi 3, 3, -1
	mtctr 4
.LBB11_1:
	bdzlr
	addi 4, 3, 1
	stb 5, 1(3)
	mr	3, 4
	b .LBB11_1
	.long	0
	.quad	0
.Lfunc_end11:
	.size	prefill_buffer, .Lfunc_end11-.Lfunc_begin11

	.p2align	2
	.type	format_ascii,@function
format_ascii:
.Lfunc_begin12:
	addi 5, 5, 1
	addi 4, 4, -1
	mtctr 5
.LBB12_1:
	bdzlr
	lbz 5, 1(4)
	addi 4, 4, 1
	addi 6, 5, -32
	clrlwi	7, 6, 24
	ld 6, 0(3)
	cmplwi	7, 95
	addi 7, 6, 1
	std 7, 0(3)
	blt	0, .LBB12_4
	li 5, 46
.LBB12_4:
	stb 5, 0(6)
	b .LBB12_1
	.long	0
	.quad	0
.Lfunc_end12:
	.size	format_ascii, .Lfunc_end12-.Lfunc_begin12

	.p2align	2
	.type	format_hex32,@function
format_hex32:
.Lfunc_begin13:
.Lfunc_gep13:
	addis 2, 12, .TOC.-.Lfunc_gep13@ha
	addi 2, 2, .TOC.-.Lfunc_gep13@l
.Lfunc_lep13:
	.localentry	format_hex32, .Lfunc_lep13-.Lfunc_gep13
	li 5, 8
	b format_hex_n
	#TC_RETURNd8 format_hex_n 0
	.long	0
	.quad	0
.Lfunc_end13:
	.size	format_hex32, .Lfunc_end13-.Lfunc_begin13

	.p2align	2
	.type	query_vuart_param,@function
query_vuart_param:
.Lfunc_begin14:
.Lfunc_gep14:
	addis 2, 12, .TOC.-.Lfunc_gep14@ha
	addi 2, 2, .TOC.-.Lfunc_gep14@l
.Lfunc_lep14:
	.localentry	query_vuart_param, .Lfunc_lep14-.Lfunc_gep14
	mflr 0
	std 22, -80(1)
	std 23, -72(1)
	std 24, -64(1)
	std 25, -56(1)
	std 26, -48(1)
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -192(1)
	ld 23, .LC0@toc(2)
	addi 28, 1, 40
	mr	25, 4
	std 0, 208(1)
	mr	24, 3
	addi 30, 1, 48
	std 30, 40(1)
	addi 4, 23, 429
	mr	3, 28
	mr	27, 7
	mr	29, 6
	mr	26, 5
	bl append_str
	mr	3, 28
	mr	4, 27
	bl append_str
	ld 3, 40(1)
	li 22, 0
	mr	4, 24
	mr	5, 25
	mr	6, 30
	stb 22, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 165
	li 6, 0
	li 7, 0
	mr	4, 24
	mr	5, 25
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lis 4, 147
	mr	25, 3
	lwz 5, 3876(4)
	addi 5, 5, 1
	stw 5, 3876(4)
	stw 3, 0(26)
	ori 3, 4, 3876
	addi 4, 23, 462
	ld 3, 76(3)
	std 3, 0(29)
	mr	3, 28
	std 30, 40(1)
	bl append_str
	mr	3, 28
	mr	4, 27
	bl append_str
	addi 4, 23, 73
	mr	3, 28
	bl append_str
	extsw 4, 25
	mr	3, 28
	bl format_s32
	addi 4, 23, 273
	mr	3, 28
	bl append_str
	ld 4, 0(29)
	mr	3, 28
	bl format_hex64
	ld 3, 40(1)
	mr	4, 25
	mr	6, 30
	stb 22, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	ld 5, 0(29)
	bl hddlog_write
	addi 1, 1, 192
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
	blr
	.long	0
	.quad	0
.Lfunc_end14:
	.size	query_vuart_param, .Lfunc_end14-.Lfunc_begin14

	.p2align	2
	.type	format_auth_request,@function
format_auth_request:
.Lfunc_begin15:
.Lfunc_gep15:
	addis 2, 12, .TOC.-.Lfunc_gep15@ha
	addi 2, 2, .TOC.-.Lfunc_gep15@l
.Lfunc_lep15:
	.localentry	format_auth_request, .Lfunc_lep15-.Lfunc_gep15
	mflr 0
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -64(1)
	li 4, 112
	li 5, 0
	std 0, 80(1)
	mr	30, 3
	li 29, 0
	bl prefill_buffer
	ori 3, 29, 64206
	li 4, 96
	stw 3, 0(30)
	li 3, 20480
	stw 3, 4(30)
	stw 4, 8(30)
	stw 4, 12(30)
	li 4, 20485
	std 4, 16(30)
	lis 4, 1032
	ori 4, 4, 1
	std 3, 24(30)
	rldic 3, 4, 34, 3
	oris 3, 3, 256
	ori 3, 3, 1
	std 3, 48(30)
	li 3, 19
	stb 29, 56(30)
	stb 3, 57(30)
	li 3, 75
	stw 3, 64(30)
	addi 1, 1, 64
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	blr
	.long	0
	.quad	0
.Lfunc_end15:
	.size	format_auth_request, .Lfunc_end15-.Lfunc_begin15

	.p2align	2
	.type	format_s32,@function
format_s32:
.Lfunc_begin16:
.Lfunc_gep16:
	addis 2, 12, .TOC.-.Lfunc_gep16@ha
	addi 2, 2, .TOC.-.Lfunc_gep16@l
.Lfunc_lep16:
	.localentry	format_s32, .Lfunc_lep16-.Lfunc_gep16
	cmpwi	4, 0
	bge 0, .LBB16_2
	ld 5, 0(3)
	neg 4, 4
	addi 6, 5, 1
	std 6, 0(3)
	li 6, 45
	stb 6, 0(5)
.LBB16_2:
	clrldi	4, 4, 32
	b format_dec
	#TC_RETURNd8 format_dec 0
	.long	0
	.quad	0
.Lfunc_end16:
	.size	format_s32, .Lfunc_end16-.Lfunc_begin16

	.p2align	2
	.type	execute_read_test,@function
execute_read_test:
.Lfunc_begin17:
.Lfunc_gep17:
	addis 2, 12, .TOC.-.Lfunc_gep17@ha
	addi 2, 2, .TOC.-.Lfunc_gep17@l
.Lfunc_lep17:
	.localentry	execute_read_test, .Lfunc_lep17-.Lfunc_gep17
	mfocrf 12, 32
	stw 12, 8(1)
	mflr 0
	stdu 1, -464(1)
	std 0, 480(1)
	std 28, 432(1)
	ld 28, 512(1)
	std 25, 408(1)
	mr	25, 3
	lis 3, 147
	std 15, 328(1)
	mr	15, 4
	li 4, 2048
	std 17, 344(1)
	mr	17, 5
	li 5, 165
	std 31, 456(1)
	ori 31, 3, 3884
	mr	3, 28
	std 14, 320(1)
	std 16, 336(1)
	mr	16, 7
	std 18, 352(1)
	std 19, 360(1)
	std 20, 368(1)
	mr	20, 6
	std 21, 376(1)
	mr	21, 10
	std 22, 384(1)
	std 23, 392(1)
	std 24, 400(1)
	std 26, 416(1)
	std 27, 424(1)
	std 29, 440(1)
	std 30, 448(1)
	std 9, 40(1)
	std 8, 48(1)
	ld 30, 552(1)
	ld 19, 544(1)
	ld 29, 520(1)
	ld 27, 504(1)
	ld 26, 496(1)
	ld 23, 536(1)
	bl prefill_buffer
	li 4, 64
	mr	3, 26
	li 5, 0
	li 18, 0
	bl prefill_buffer
	ld 22, .LC0@toc(2)
	li 3, 40
	li 4, 12
	stb 3, 0(26)
	li 3, 1
	addi 14, 1, 56
	stb 18, 2(26)
	addi 24, 1, 64
	stb 18, 3(26)
	stb 18, 4(26)
	stb 15, 5(26)
	stb 3, 8(26)
	stw 4, 32(26)
	addi 4, 22, 29
	stw 17, 36(26)
	stw 20, 40(26)
	stw 16, 44(26)
	stw 3, 48(26)
	mr	3, 14
	std 29, 56(26)
	std 24, 56(1)
	bl append_str
	mr	3, 14
	mr	4, 21
	bl append_str
	addi 4, 22, 161
	mr	3, 14
	bl append_str
	mr	3, 14
	mr	4, 15
	mr	15, 25
	bl format_dec
	addi 4, 22, 297
	mr	3, 14
	bl append_str
	mr	3, 14
	mr	4, 16
	bl format_dec
	addi 4, 22, 168
	mr	3, 14
	bl append_str
	mr	3, 14
	mr	4, 17
	bl format_dec
	addi 4, 22, 85
	mr	3, 14
	bl append_str
	mr	3, 14
	mr	4, 20
	bl format_dec
	ld 3, 56(1)
	mr	4, 27
	mr	5, 29
	mr	6, 24
	stb 18, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 25
	mr	6, 27
	li 7, 64
	mr	8, 29
	li 9, 2048
	bl lv1_hcall
	nop
	mr	20, 3
	lwz 3, -8(31)
	cmpldi	20, 0
	addi 3, 3, 1
	stw 3, -8(31)
	stw 20, 0(23)
	beq	0, .LBB17_5
	lwz 3, 0(31)
	cmplwi	3, 0
	bne	0, .LBB17_3
	ld 3, 48(1)
	stw 3, 0(31)
.LBB17_3:
	lwz 3, 4(31)
	mr	16, 30
	mr	30, 19
	cmplwi	3, 0
	bne	0, .LBB17_7
	stw 20, 4(31)
	b .LBB17_7
.LBB17_5:
	ld 17, 560(1)
	mr	3, 15
	mr	5, 19
	mr	6, 30
	ld 25, 40(1)
	mr	7, 17
	ld 4, 68(31)
	bl poll_completion
	cmplwi	3, 0
	mr	16, 30
	mr	30, 19
	beq	0, .LBB17_7
	lwz 3, -4(31)
	addi 30, 1, 56
	addi 4, 22, 409
	or 3, 3, 25
	stw 3, -4(31)
	ld 3, 48(1)
	stw 3, 0(31)
	mr	3, 30
	std 24, 56(1)
	bl append_str
	mr	3, 30
	mr	4, 21
	bl append_str
	addi 4, 22, 1249
	mr	3, 30
	bl append_str
	ld 3, 56(1)
	li 4, 0
	mr	6, 24
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 0(16)
	ld 5, 0(17)
	bl hddlog_write
	li 3, 1
	b .LBB17_22
.LBB17_7:
	li 3, 2049
	ld 4, 568(1)
	cmpdi 2, 20, 0
	addi 5, 28, -1
	ld 19, 528(1)
	li 17, 0
	mtctr 3
	ld 3, 576(1)
	bdz .LBB17_9
.LBB17_8:
	lbz 6, 1(5)
	addi 5, 5, 1
	xori 6, 6, 165
	cntlzw	6, 6
	srwi 6, 6, 5
	add 17, 17, 6
	bdnz .LBB17_8
.LBB17_9:
	cmplwi	17, 2048
	li 23, 0
	stw 17, 0(4)
	beq	0, .LBB17_19
	lbz 4, 1(28)
	cmplwi	4, 67
	bne	0, .LBB17_15
	lbz 4, 2(28)
	cmplwi	4, 68
	bne	0, .LBB17_15
	lbz 4, 3(28)
	cmplwi	4, 48
	bne	0, .LBB17_15
	lbz 4, 4(28)
	cmplwi	4, 48
	bne	0, .LBB17_15
	lbz 4, 5(28)
	li 23, 2
	cmplwi	4, 49
	beq	0, .LBB17_19
.LBB17_15:
	li 4, 2049
	addi 5, 28, -1
	mtctr 4
	li 4, 0
	bdz .LBB17_17
.LBB17_16:
	lbz 6, 1(5)
	addi 5, 5, 1
	cntlzw	6, 6
	srwi 6, 6, 5
	add 4, 4, 6
	bdnz .LBB17_16
.LBB17_17:
	cmplwi	4, 2048
	li 23, 1
	beq	0, .LBB17_19
	li 23, 3
.LBB17_19:
	addi 18, 1, 56
	stb 23, 0(3)
	addi 4, 22, 91
	mr	3, 18
	std 24, 56(1)
	bl append_str
	mr	3, 18
	mr	4, 21
	bl append_str
	addi 4, 22, 73
	mr	3, 18
	bl append_str
	clrldi	4, 20, 32
	mr	3, 18
	bl format_dec
	addi 4, 22, 389
	mr	3, 18
	bl append_str
	ld 4, 0(30)
	mr	3, 18
	bl format_hex64
	addi 4, 22, 97
	mr	3, 18
	bl append_str
	rldic 3, 23, 3, 29
	add 3, 22, 3
	ld 4, 1280(3)
	mr	3, 18
	bl append_str
	addi 4, 22, 34
	mr	3, 18
	bl append_str
	clrldi	4, 17, 32
	mr	3, 18
	bl format_dec
	addi 4, 22, 225
	mr	3, 18
	bl append_str
	lwz 4, 0(16)
	mr	3, 18
	bl format_dec
	addi 4, 22, 39
	mr	3, 18
	bl append_str
	mr	3, 18
	mr	4, 28
	bl format_bytes_hex
	addi 4, 22, 103
	mr	3, 18
	bl append_str
	addi 4, 28, 16
	mr	3, 18
	bl format_bytes_hex
	addi 4, 22, 175
	mr	3, 18
	bl append_str
	addi 4, 28, 40
	mr	3, 18
	li 5, 8
	bl format_ascii
	mr	3, 18
	mr	4, 22
	bl append_str
	ld 3, 56(1)
	li 4, 0
	mr	6, 24
	stb 4, 0(3)
	lis 3, 20559
	mr	4, 20
	ori 3, 3, 21332
	ld 5, 0(30)
	bl hddlog_write
	bc 4, 10, .LBB17_21
	ld 3, 0(30)
	clrldi	3, 3, 56
	cmpldi	3, 2
	li 3, 0
	bne	0, .LBB17_22
.LBB17_21:
	mr	3, 15
	mr	4, 26
	mr	5, 27
	mr	6, 28
	mr	7, 29
	mr	8, 19
	bl do_request_sense
	li 3, -1
.LBB17_22:
	ld 31, 456(1)
	ld 30, 448(1)
	ld 29, 440(1)
	ld 28, 432(1)
	ld 27, 424(1)
	ld 26, 416(1)
	ld 25, 408(1)
	ld 24, 400(1)
	ld 23, 392(1)
	ld 22, 384(1)
	ld 21, 376(1)
	ld 20, 368(1)
	ld 19, 360(1)
	ld 18, 352(1)
	ld 17, 344(1)
	ld 16, 336(1)
	ld 15, 328(1)
	ld 14, 320(1)
	addi 1, 1, 464
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	blr
	.long	0
	.quad	0
.Lfunc_end17:
	.size	execute_read_test, .Lfunc_end17-.Lfunc_begin17

	.p2align	2
	.type	format_hex_n,@function
format_hex_n:
.Lfunc_begin18:
.Lfunc_gep18:
	addis 2, 12, .TOC.-.Lfunc_gep18@ha
	addi 2, 2, .TOC.-.Lfunc_gep18@l
.Lfunc_lep18:
	.localentry	format_hex_n, .Lfunc_lep18-.Lfunc_gep18
	ld 6, .LC0@toc(2)
	addi 7, 5, 1
	rlwinm 5, 5, 2, 0, 29
	mtctr 7
.LBB18_1:
	addi 5, 5, -4
	bdzlr
	srd 7, 4, 5
	ld 8, 0(3)
	clrldi	7, 7, 60
	add 7, 6, 7
	lbz 7, 819(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB18_1
	.long	0
	.quad	0
.Lfunc_end18:
	.size	format_hex_n, .Lfunc_end18-.Lfunc_begin18

	.p2align	2
	.type	format_bytes_hex,@function
format_bytes_hex:
.Lfunc_begin19:
.Lfunc_gep19:
	addis 2, 12, .TOC.-.Lfunc_gep19@ha
	addi 2, 2, .TOC.-.Lfunc_gep19@l
.Lfunc_lep19:
	.localentry	format_bytes_hex, .Lfunc_lep19-.Lfunc_gep19
	ld 6, .LC0@toc(2)
	li 5, 17
	mtctr 5
	addi 5, 4, -1
	addi 4, 6, 819
.LBB19_1:
	bdzlr
	lbz 6, 1(5)
	ld 7, 0(3)
	rldicl 6, 6, 60, 4
	lbzx 6, 4, 6
	addi 8, 7, 1
	std 8, 0(3)
	stb 6, 0(7)
	lbz 6, 1(5)
	addi 5, 5, 1
	ld 7, 0(3)
	clrldi	6, 6, 60
	lbzx 6, 4, 6
	addi 8, 7, 1
	std 8, 0(3)
	stb 6, 0(7)
	b .LBB19_1
	.long	0
	.quad	0
.Lfunc_end19:
	.size	format_bytes_hex, .Lfunc_end19-.Lfunc_begin19

	.p2align	2
	.type	do_request_sense,@function
do_request_sense:
.Lfunc_begin20:
.Lfunc_gep20:
	addis 2, 12, .TOC.-.Lfunc_gep20@ha
	addi 2, 2, .TOC.-.Lfunc_gep20@l
.Lfunc_lep20:
	.localentry	do_request_sense, .Lfunc_lep20-.Lfunc_gep20
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
	stdu 1, -256(1)
	mr	28, 7
	mr	27, 6
	std 0, 272(1)
	mr	6, 4
	mr	30, 8
	mr	25, 5
	mr	26, 3
	li 4, 3
	li 5, 18
	mr	3, 6
	li 6, 1
	li 7, 1
	mr	8, 28
	lis 21, 147
	bl setup_atapi_block
	li 4, 18
	mr	3, 27
	li 5, 0
	li 23, 0
	bl prefill_buffer
	ld 22, .LC0@toc(2)
	addi 24, 1, 32
	addi 29, 1, 40
	std 29, 32(1)
	mr	3, 24
	addi 4, 22, 1065
	bl append_str
	mr	3, 24
	mr	4, 25
	bl format_hex64
	addi 4, 22, 524
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 28
	bl format_hex64
	ld 3, 32(1)
	mr	4, 25
	mr	5, 28
	mr	6, 29
	stb 23, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 26
	mr	6, 25
	li 7, 64
	mr	8, 28
	li 9, 18
	bl lv1_hcall
	nop
	mr	28, 3
	lwz 3, 3876(21)
	cmpldi	28, 0
	addi 3, 3, 1
	stw 3, 3876(21)
	stw 28, 1656(30)
	beq	0, .LBB20_2
.LBB20_1:
	addi 27, 1, 32
	addi 4, 22, 769
	std 29, 32(1)
	mr	3, 27
	bl append_str
	clrldi	4, 28, 32
	mr	3, 27
	bl format_dec
	addi 4, 22, 389
	mr	3, 27
	bl append_str
	ld 4, 1848(30)
	mr	3, 27
	bl format_hex64
	addi 4, 22, 371
	mr	3, 27
	bl append_str
	lbz 3, 1958(30)
	clrldi	4, 3, 60
	mr	3, 27
	bl format_hex32
	addi 4, 22, 313
	mr	3, 27
	bl append_str
	lbz 4, 1968(30)
	mr	3, 27
	bl format_hex32
	addi 4, 22, 380
	mr	3, 27
	bl append_str
	lbz 4, 1969(30)
	mr	3, 27
	bl format_hex32
	ld 3, 32(1)
	mr	4, 28
	stb 23, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	ld 5, 1848(30)
	b .LBB20_4
.LBB20_2:
	ori 25, 21, 3876
	addi 5, 30, 1848
	ld 4, 76(25)
	addi 6, 30, 1708
	addi 7, 30, 1912
	mr	3, 26
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB20_5
	lwz 3, 4(25)
	addi 4, 22, 1112
	ori 3, 3, 128
	stw 3, 4(25)
	addi 3, 1, 32
	std 29, 32(1)
	bl append_str
	ld 3, 32(1)
	li 4, 0
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 1708(30)
	ld 5, 1912(30)
.LBB20_4:
	mr	6, 29
	bl hddlog_write
	addi 1, 1, 256
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
.LBB20_5:
	li 3, 19
	addi 4, 27, -1
	mtctr 3
	addi 5, 30, 1955
	li 3, 0
	bdz .LBB20_1
.LBB20_6:
	lbz 6, 1(4)
	addi 7, 5, 1
	addi 4, 4, 1
	addi 3, 3, 1
	stb 6, 1(5)
	mr	5, 7
	bdnz .LBB20_6
	b .LBB20_1
	.long	0
	.quad	0
.Lfunc_end20:
	.size	do_request_sense, .Lfunc_end20-.Lfunc_begin20

	.type	.L_MergedGlobals,@object
	.section	.data.rel.ro,"aw",@progbits
	.p2align	3, 0x0
.L_MergedGlobals:
	.asciz	"'"
	.asciz	"p2"
	.asciz	"OK"
	.asciz	"p10"
	.asciz	" W="
	.asciz	" R="
	.asciz	"HC="
	.asciz	"NONE"
	.asciz	"pre "
	.asciz	" a5="
	.asciz	" w0="
	.asciz	" WR="
	.asciz	" hdd="
	.asciz	" blk="
	.asciz	" vrd="
	.asciz	"pio_0"
	.asciz	": rc="
	.asciz	"SHORT"
	.asciz	" bsz="
	.asciz	"post "
	.asciz	" cls="
	.asciz	" w16="
	.asciz	"ZEROS"
	.asciz	"OTHER"
	.asciz	" P10="
	.asciz	" LOG="
	.asciz	"p10_p0"
	.asciz	"pio_16"
	.asciz	"pio_17"
	.asciz	"dma_16"
	.asciz	": lba="
	.asciz	" blks="
	.asciz	" vol='"
	.asciz	" ST=0x"
	.asciz	" FL=0x"
	.asciz	" PVD: "
	.asciz	" SKIP="
	.asciz	" 0_A5="
	.asciz	" rgn=0x"
	.asciz	" polls="
	.asciz	" ticks="
	.asciz	" resp='"
	.asciz	" lba=0x"
	.asciz	" bytes="
	.asciz	" flg=0x"
	.asciz	" val=0x"
	.asciz	"TIMEOUT"
	.asciz	"SKIPPED"
	.asciz	" proto="
	.asciz	"DATA_OK"
	.asciz	" asc=0x"
	.asciz	" POLLS="
	.asciz	" TMO=0x"
	.asciz	" 17_A5="
	.asciz	" BUS=0x"
	.asciz	" stat=0x"
	.asciz	"ERR_STAT"
	.asciz	" skey=0x"
	.asciz	" ascq=0x"
	.asciz	" async=0x"
	.asciz	"WRITE_ERR"
	.asciz	"timeout: "
	.asciz	"UNCHANGED"
	.asciz	"pre vuart_"
	.asciz	"VUART: P2="
	.asciz	"DMA RGN=0x"
	.asciz	"post vuart_"
	.asciz	"AUTH BYTES="
	.asciz	"PIO: 16_A5="
	.asciz	" bus=4 dev=2"
	.asciz	" bus_addr=0x"
	.asciz	" buf_lpar=0x"
	.asciz	"step failed="
	.asciz	"post map: rc="
	.asciz	"post tur: rc="
	.asciz	"post inq: rc="
	.asciz	"post cap: rc="
	.asciz	" len=0x100000"
	.asciz	"clean success"
	.asciz	"P11-W1 AUTH: "
	.asciz	"CDVD LPAR: 0x"
	.asciz	"scan: rom_cnt="
	.asciz	"post open: rc="
	.asciz	"post free: rc="
	.asciz	"P11-W1 PIO16: "
	.asciz	"P11-W1 RUNNING"
	.asciz	"post unmap: rc="
	.asciz	"post close: rc="
	.asciz	"post sense: rc="
	.asciz	"pre map: lpar=0x"
	.asciz	"pre free: rgn=0x"
	.asciz	"0123456789abcdef"
	.asciz	"pre unmap: rgn=0x"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"post dma_alloc: rc="
	.asciz	"pre tur: cmd_lpar=0x"
	.asciz	"pre inq: cmd_lpar=0x"
	.asciz	"pre cap: cmd_lpar=0x"
	.asciz	"post auth_write: rc="
	.asciz	"pre open: bus=4 dev=2"
	.asciz	"post auth_read: read="
	.asciz	"pre close: bus=4 dev=2"
	.asciz	"pre sense: cmd_lpar=0x"
	.asciz	"boot: ps2_netemu_p11_W1"
	.asciz	"timeout: sense timed out"
	.asciz	"auth skipped: guard failed"
	.asciz	"finish: ps2_netemu_p11_W1 "
	.asciz	"post dma_alloc: rc=0 rgn=0x"
	.asciz	"grd ok: lpar & ea sanity pass"
	.asciz	" timed out; halting hypercalls"
	.quad	.L_MergedGlobals+419
	.quad	.L_MergedGlobals+109
	.quad	.L_MergedGlobals+305
	.quad	.L_MergedGlobals+115
	.asciz	"grd reject: sanity failed (0 hc)"
	.asciz	"pre auth_write: port=10 len=0x70"
	.asciz	"pre dma_alloc: sz=0x100000 pexp=20"
	.asciz	"pre auth_read: port=10 max_len=0x70"
	.asciz	"finish: ps2_netemu_p9_U1 failed step=1"
	.asciz	"timeout: tur timed out; halting hypercalls"
	.asciz	"timeout: inq timed out; halting hypercalls"
	.asciz	"timeout: cap timed out; halting hypercalls"
	.space	7
	.quad	.L_MergedGlobals+24
	.quad	.L_MergedGlobals+5
	.quad	.L_MergedGlobals+362
	.quad	.L_MergedGlobals+281
	.quad	.L_MergedGlobals+79
	.quad	.L_MergedGlobals+289
	.quad	.L_MergedGlobals+399
	.size	.L_MergedGlobals, 1680

.L.str.27 = .L_MergedGlobals
	.size	.L.str.27, 2
.L.str.33 = .L_MergedGlobals+2
	.size	.L.str.33, 3
.L.str.64 = .L_MergedGlobals+5
	.size	.L.str.64, 3
.L.str.34 = .L_MergedGlobals+8
	.size	.L.str.34, 4
.L.str.103 = .L_MergedGlobals+12
	.size	.L.str.103, 4
.L.str.104 = .L_MergedGlobals+16
	.size	.L.str.104, 4
.L.str.105 = .L_MergedGlobals+20
	.size	.L.str.105, 4
.L.str.63 = .L_MergedGlobals+24
	.size	.L.str.63, 5
.L.str.70 = .L_MergedGlobals+29
	.size	.L.str.70, 5
.L.str.79 = .L_MergedGlobals+34
	.size	.L.str.79, 5
.L.str.80 = .L_MergedGlobals+39
	.size	.L.str.80, 5
.L.str.100 = .L_MergedGlobals+44
	.size	.L.str.100, 5
.L.str.2 = .L_MergedGlobals+49
	.size	.L.str.2, 6
.L.str.32 = .L_MergedGlobals+55
	.size	.L.str.32, 6
.L.str.44 = .L_MergedGlobals+61
	.size	.L.str.44, 6
.L.str.46 = .L_MergedGlobals+67
	.size	.L.str.46, 6
.L.str.61 = .L_MergedGlobals+73
	.size	.L.str.61, 6
.L.str.67 = .L_MergedGlobals+79
	.size	.L.str.67, 6
.L.str.74 = .L_MergedGlobals+85
	.size	.L.str.74, 6
.L.str.77 = .L_MergedGlobals+91
	.size	.L.str.77, 6
.L.str.78 = .L_MergedGlobals+97
	.size	.L.str.78, 6
.L.str.81 = .L_MergedGlobals+103
	.size	.L.str.81, 6
.L.str.84 = .L_MergedGlobals+109
	.size	.L.str.84, 6
.L.str.86 = .L_MergedGlobals+115
	.size	.L.str.86, 6
.L.str.102 = .L_MergedGlobals+121
	.size	.L.str.102, 6
.L.str.106 = .L_MergedGlobals+127
	.size	.L.str.106, 6
.L.str.35 = .L_MergedGlobals+133
	.size	.L.str.35, 7
.L.str.45 = .L_MergedGlobals+140
	.size	.L.str.45, 7
.L.str.47 = .L_MergedGlobals+147
	.size	.L.str.47, 7
.L.str.48 = .L_MergedGlobals+154
	.size	.L.str.48, 7
.L.str.71 = .L_MergedGlobals+161
	.size	.L.str.71, 7
.L.str.73 = .L_MergedGlobals+168
	.size	.L.str.73, 7
.L.str.82 = .L_MergedGlobals+175
	.size	.L.str.82, 7
.L.str.94 = .L_MergedGlobals+182
	.size	.L.str.94, 7
.L.str.95 = .L_MergedGlobals+189
	.size	.L.str.95, 7
.L.str.97 = .L_MergedGlobals+196
	.size	.L.str.97, 7
.L.str.107 = .L_MergedGlobals+203
	.size	.L.str.107, 7
.L.str.110 = .L_MergedGlobals+210
	.size	.L.str.110, 7
.L.str.13 = .L_MergedGlobals+217
	.size	.L.str.13, 8
.L.str.20 = .L_MergedGlobals+225
	.size	.L.str.20, 8
.L.str.21 = .L_MergedGlobals+233
	.size	.L.str.21, 8
.L.str.26 = .L_MergedGlobals+241
	.size	.L.str.26, 8
.L.str.31 = .L_MergedGlobals+249
	.size	.L.str.31, 8
.L.str.39 = .L_MergedGlobals+257
	.size	.L.str.39, 8
.L.str.43 = .L_MergedGlobals+265
	.size	.L.str.43, 8
.L.str.62 = .L_MergedGlobals+273
	.size	.L.str.62, 8
.L.str.66 = .L_MergedGlobals+281
	.size	.L.str.66, 8
.L.str.68 = .L_MergedGlobals+289
	.size	.L.str.68, 8
.L.str.72 = .L_MergedGlobals+297
	.size	.L.str.72, 8
.L.str.85 = .L_MergedGlobals+305
	.size	.L.str.85, 8
.L.str.91 = .L_MergedGlobals+313
	.size	.L.str.91, 8
.L.str.99 = .L_MergedGlobals+321
	.size	.L.str.99, 8
.L.str.108 = .L_MergedGlobals+329
	.size	.L.str.108, 8
.L.str.111 = .L_MergedGlobals+337
	.size	.L.str.111, 8
.L.str.114 = .L_MergedGlobals+345
	.size	.L.str.114, 8
.L.str.42 = .L_MergedGlobals+353
	.size	.L.str.42, 9
.L.str.65 = .L_MergedGlobals+362
	.size	.L.str.65, 9
.L.str.90 = .L_MergedGlobals+371
	.size	.L.str.90, 9
.L.str.92 = .L_MergedGlobals+380
	.size	.L.str.92, 9
.L.str.19 = .L_MergedGlobals+389
	.size	.L.str.19, 10
.L.str.69 = .L_MergedGlobals+399
	.size	.L.str.69, 10
.L.str.75 = .L_MergedGlobals+409
	.size	.L.str.75, 10
.L.str.83 = .L_MergedGlobals+419
	.size	.L.str.83, 10
.L.str.59 = .L_MergedGlobals+429
	.size	.L.str.59, 11
.L.str.101 = .L_MergedGlobals+440
	.size	.L.str.101, 11
.L.str.113 = .L_MergedGlobals+451
	.size	.L.str.113, 11
.L.str.60 = .L_MergedGlobals+462
	.size	.L.str.60, 12
.L.str.98 = .L_MergedGlobals+474
	.size	.L.str.98, 12
.L.str.109 = .L_MergedGlobals+486
	.size	.L.str.109, 12
.L.str.3 = .L_MergedGlobals+498
	.size	.L.str.3, 13
.L.str.15 = .L_MergedGlobals+511
	.size	.L.str.15, 13
.L.str.23 = .L_MergedGlobals+524
	.size	.L.str.23, 13
.L.str.58 = .L_MergedGlobals+537
	.size	.L.str.58, 13
.L.str.14 = .L_MergedGlobals+550
	.size	.L.str.14, 14
.L.str.18 = .L_MergedGlobals+564
	.size	.L.str.18, 14
.L.str.25 = .L_MergedGlobals+578
	.size	.L.str.25, 14
.L.str.30 = .L_MergedGlobals+592
	.size	.L.str.30, 14
.L.str.50 = .L_MergedGlobals+606
	.size	.L.str.50, 14
.L.str.57 = .L_MergedGlobals+620
	.size	.L.str.57, 14
.L.str.93 = .L_MergedGlobals+634
	.size	.L.str.93, 14
.L.str.112 = .L_MergedGlobals+648
	.size	.L.str.112, 14
.L.str.1 = .L_MergedGlobals+662
	.size	.L.str.1, 15
.L.str.8 = .L_MergedGlobals+677
	.size	.L.str.8, 15
.L.str.53 = .L_MergedGlobals+692
	.size	.L.str.53, 15
.L.str.96 = .L_MergedGlobals+707
	.size	.L.str.96, 15
.L.str.115 = .L_MergedGlobals+722
	.size	.L.str.115, 15
.L.str.51 = .L_MergedGlobals+737
	.size	.L.str.51, 16
.L.str.55 = .L_MergedGlobals+753
	.size	.L.str.55, 16
.L.str.89 = .L_MergedGlobals+769
	.size	.L.str.89, 16
.L.str.12 = .L_MergedGlobals+785
	.size	.L.str.12, 17
.L.str.52 = .L_MergedGlobals+802
	.size	.L.str.52, 17
HEX_DIGITS = .L_MergedGlobals+819
	.size	HEX_DIGITS, 17
.L.str.49 = .L_MergedGlobals+836
	.size	.L.str.49, 18
hddlog_init.path = .L_MergedGlobals+854
	.size	hddlog_init.path, 20
hddlog_write.path = .L_MergedGlobals+874
	.size	hddlog_write.path, 20
.L.str.10 = .L_MergedGlobals+894
	.size	.L.str.10, 20
.L.str.16 = .L_MergedGlobals+914
	.size	.L.str.16, 21
.L.str.22 = .L_MergedGlobals+935
	.size	.L.str.22, 21
.L.str.28 = .L_MergedGlobals+956
	.size	.L.str.28, 21
.L.str.38 = .L_MergedGlobals+977
	.size	.L.str.38, 21
.L.str.7 = .L_MergedGlobals+998
	.size	.L.str.7, 22
.L.str.41 = .L_MergedGlobals+1020
	.size	.L.str.41, 22
.L.str.54 = .L_MergedGlobals+1042
	.size	.L.str.54, 23
.L.str.87 = .L_MergedGlobals+1065
	.size	.L.str.87, 23
.L.str = .L_MergedGlobals+1088
	.size	.L.str, 24
.L.str.88 = .L_MergedGlobals+1112
	.size	.L.str.88, 25
.L.str.36 = .L_MergedGlobals+1137
	.size	.L.str.36, 27
.L.str.56 = .L_MergedGlobals+1164
	.size	.L.str.56, 27
.L.str.11 = .L_MergedGlobals+1191
	.size	.L.str.11, 28
.L.str.6 = .L_MergedGlobals+1219
	.size	.L.str.6, 30
.L.str.76 = .L_MergedGlobals+1249
	.size	.L.str.76, 31
class_to_str.STRS = .L_MergedGlobals+1280
	.size	class_to_str.STRS, 32
.L.str.4 = .L_MergedGlobals+1312
	.size	.L.str.4, 33
.L.str.37 = .L_MergedGlobals+1345
	.size	.L.str.37, 33
.L.str.9 = .L_MergedGlobals+1378
	.size	.L.str.9, 35
.L.str.40 = .L_MergedGlobals+1413
	.size	.L.str.40, 36
.L.str.5 = .L_MergedGlobals+1449
	.size	.L.str.5, 39
.L.str.17 = .L_MergedGlobals+1488
	.size	.L.str.17, 43
.L.str.24 = .L_MergedGlobals+1531
	.size	.L.str.24, 43
.L.str.29 = .L_MergedGlobals+1574
	.size	.L.str.29, 43
auth_verdict_to_str.STRS = .L_MergedGlobals+1624
	.size	auth_verdict_to_str.STRS, 56
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
