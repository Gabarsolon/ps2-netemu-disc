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
	addi 4, 3, 818
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
	addi 4, 3, 838
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
	mflr 0
	stdu 1, -592(1)
	cmplwi	3, 8
	std 0, 608(1)
	lis 4, 147
	std 27, 552(1)
	li 27, 0
	std 14, 448(1)
	std 15, 456(1)
	std 16, 464(1)
	std 17, 472(1)
	std 18, 480(1)
	std 19, 488(1)
	std 20, 496(1)
	std 21, 504(1)
	std 22, 512(1)
	std 23, 520(1)
	std 24, 528(1)
	std 25, 536(1)
	std 26, 544(1)
	std 28, 560(1)
	std 29, 568(1)
	std 30, 576(1)
	std 31, 584(1)
	bgt	0, .LBB3_2
	mr	27, 3
.LBB3_2:
	ori 15, 4, 3876
	bl get_arena
	cmpldi	3, 0
	beq	0, .LBB3_18
	mr	17, 3
.LBB3_4:
	bl native_clock
	nop
	ld 4, 60(15)
	lis 5, 1826
	cmpdi	4, 0
	std 3, 60(15)
	sub	3, 3, 4
	ori 4, 5, 31264
	bc 12, 2, .LBB3_7
	cmpld	3, 4
	bc 4, 1, .LBB3_7
	lwz 3, 16(15)
	addi 3, 3, 1
	stw 3, 16(15)
.LBB3_7:
	lwz 3, -4(15)
	addi 31, 1, 192
	andi. 3, 3, 2
	bne	0, .LBB3_38
	lis 3, 1122
	std 17, 144(1)
	ori 3, 3, 30067
	rotldi	26, 3, 40
	std 27, 136(1)
	bl hddlog_init
	ld 3, .LC0@toc(2)
	std 31, 184(1)
	std 3, 128(1)
	addi 4, 3, 1074
	addi 3, 1, 184
	bl append_str
	ld 3, 184(1)
	li 17, 0
	li 4, 2072
	li 5, 1
	mr	6, 31
	stb 17, 0(3)
	lis 3, 16975
	mr	14, 31
	ori 3, 3, 20308
	bl hddlog_write
	lis 3, 50
	lis 5, 29285
	lis 4, 29817
	ori 3, 3, 12987
	ori 5, 5, 26473
	ori 4, 4, 28773
	rldic 28, 3, 41, 1
	rldic 3, 5, 32, 1
	li 16, 9
	li 29, 2
	li 18, 0
	addi 25, 1, 176
	addi 24, 1, 168
	addi 23, 1, 160
	addi 22, 1, 152
	li 27, 0
	rldic 21, 4, 32, 1
	oris 20, 3, 28526
	li 30, 0
	li 31, 0
.LBB3_9:
	addi 16, 16, -1
	cmpldi	16, 0
	bc 4, 1, .LBB3_22
	add 19, 27, 28
	mr	3, 25
	std 17, 176(1)
	mr	4, 24
	mr	5, 26
	std 17, 168(1)
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
	ld 3, 176(1)
	addi 30, 30, 1
	cmpldi	3, 0
	beq	0, .LBB3_17
	cmpldi	3, 5
	bne	0, .LBB3_11
	mr	3, 23
	mr	4, 22
	std 17, 160(1)
	mr	5, 26
	mr	6, 19
	std 17, 152(1)
	mr	7, 20
	li 8, 0
	bl repo_read
	nop
	cmpldi	3, 0
	bne	0, .LBB3_16
	ld 3, 160(1)
	ld 4, 144(1)
	stw 3, 1660(4)
.LBB3_16:
	addi 31, 31, 1
	mr	29, 27
	b .LBB3_11
.LBB3_17:
	li 18, 1
	b .LBB3_11
.LBB3_18:
	lwz 3, -4(15)
	andi. 3, 3, 8
	lis 3, 48
	ori 28, 3, 20160
	bne	0, .LBB3_62
	lwz 3, -4(15)
	li 4, 3
	li 5, 0
	li 30, 0
	ori 3, 3, 1
	stw 3, -4(15)
	li 3, 4096
	bl native_alloc
	nop
	mr	17, 3
	bl arena_rw
	cmplwi	3, 0
	beq	0, .LBB3_26
	std 17, 20(15)
	lwz 3, -4(15)
	ori 3, 3, 4
	stw 3, -4(15)
	li 3, 2073
	mtctr 3
	addi 3, 17, -1
	bdz .LBB3_4
.LBB3_21:
	addi 4, 3, 1
	stb 30, 1(3)
	mr	3, 4
	bdnz .LBB3_21
	b .LBB3_4
.LBB3_22:
	ld 17, 144(1)
	lis 3, 18258
	addi 25, 1, 184
	ori 26, 3, 17440
	mr	3, 25
	stw 30, 1664(17)
	stw 31, 36(15)
	stw 18, 40(15)
	ld 28, 128(1)
	addi 4, 28, 584
	std 14, 184(1)
	bl append_str
	clrldi	24, 31, 32
	mr	3, 25
	mr	4, 24
	mr	31, 14
	bl format_dec
	addi 4, 28, 41
	mr	3, 25
	bl append_str
	clrldi	23, 18, 32
	mr	3, 25
	mr	4, 23
	bl format_dec
	addi 4, 28, 420
	mr	3, 25
	bl append_str
	ld 3, 184(1)
	li 22, 0
	mr	4, 24
	mr	5, 23
	mr	6, 14
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
	addi 27, 1, 184
	stw 3, 8(15)
	li 3, -1
	addi 4, 28, 1355
	stw 3, 12(15)
	mr	3, 27
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	mr	4, 24
	mr	5, 23
	mr	6, 31
	stb 22, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 28, 1457
	mr	3, 27
	std 31, 184(1)
	bl append_str
	b .LBB3_37
.LBB3_24:
	addi 25, 1, 184
	std 24, 1760(17)
	addi 4, 28, 1263
	std 23, 1768(17)
	std 3, 1776(17)
	mr	3, 25
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	mr	4, 24
	mr	5, 23
	mr	6, 31
	stb 22, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 28, 961
	mr	3, 25
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 4
	mr	5, 29
	mr	6, 31
	mr	27, 29
	stb 22, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 170
	li 4, 4
	li 6, 0
	li 7, 0
	mr	5, 29
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	26, 3
	mr	3, 25
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 599
	stw 26, 1604(17)
	std 31, 184(1)
	bl append_str
	clrldi	4, 26, 32
	mr	3, 25
	bl format_dec
	ld 3, 184(1)
	mr	4, 26
	li 5, 0
	mr	6, 31
	stb 22, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	bl hddlog_write
	cmpldi	26, 0
	beq	0, .LBB3_27
	li 3, 2
	stw 3, 8(15)
	stw 26, 12(15)
	b .LBB3_34
.LBB3_26:
	lwz 3, -4(15)
	ori 3, 3, 8
	stw 3, -4(15)
	b .LBB3_62
.LBB3_27:
	lis 3, 20562
	lis 4, 20559
	std 31, 184(1)
	ori 25, 3, 17696
	ori 26, 4, 21332
	addi 4, 28, 1422
	addi 3, 1, 184
	bl append_str
	ld 3, 184(1)
	li 18, 0
	lis 4, 16
	li 5, 20
	mr	6, 31
	stb 18, 0(3)
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
	lwz 3, 0(15)
	cmpldi	22, 0
	addi 3, 3, 1
	stw 3, 0(15)
	stw 22, 1608(17)
	beq	0, .LBB3_29
	addi 24, 1, 184
	addi 4, 28, 858
	std 31, 184(1)
	mr	3, 24
	bl append_str
	clrldi	4, 22, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 22
	li 5, 0
	mr	6, 31
	stb 18, 0(3)
	mr	3, 26
	bl hddlog_write
	li 3, 3
	stw 3, 8(15)
	stw 22, 12(15)
	b .LBB3_32
.LBB3_29:
	ld 22, 76(15)
	addi 21, 1, 184
	addi 4, 28, 1150
	mr	3, 21
	std 22, 1744(17)
	std 31, 184(1)
	bl append_str
	mr	3, 21
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	li 4, 0
	mr	5, 22
	mr	6, 31
	stb 18, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 28, 692
	mr	3, 21
	std 31, 184(1)
	bl append_str
	mr	3, 21
	mr	4, 24
	bl format_hex64
	addi 4, 28, 183
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	mr	4, 24
	mr	5, 22
	mr	6, 31
	stb 18, 0(3)
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
	li 30, 4
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	20, 3
	mr	3, 21
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 472
	stw 20, 1612(17)
	ld 19, 76(15)
	std 19, 1752(17)
	std 31, 184(1)
	bl append_str
	clrldi	4, 20, 32
	mr	3, 21
	bl format_dec
	addi 4, 28, 433
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 19
	bl format_hex64
	ld 3, 184(1)
	mr	4, 20
	mr	5, 19
	mr	6, 31
	stb 18, 0(3)
	mr	3, 26
	bl hddlog_write
	cmpldi	20, 0
	beq	0, .LBB3_67
	stw 30, 8(15)
	stw 20, 12(15)
.LBB3_31:
	addi 24, 1, 184
	addi 4, 28, 709
	std 31, 184(1)
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	li 30, 0
	mr	4, 22
	li 5, 0
	mr	6, 31
	stb 30, 0(3)
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
	lwz 4, 0(15)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 614
	stw 3, 1620(17)
	mr	3, 24
	std 31, 184(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 23
	li 5, 0
	mr	6, 31
	stb 30, 0(3)
	mr	3, 26
	bl hddlog_write
.LBB3_32:
	addi 24, 1, 184
	addi 4, 28, 1028
	std 31, 184(1)
	mr	3, 24
	bl append_str
	ld 3, 184(1)
	li 30, 0
	li 4, 4
	mr	5, 27
	mr	6, 31
	stb 30, 0(3)
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
	lwz 4, 0(15)
	mr	27, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 660
	stw 3, 1624(17)
	mr	3, 24
	std 31, 184(1)
	bl append_str
	clrldi	4, 27, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 27
	li 5, 0
	stb 30, 0(3)
	mr	3, 26
.LBB3_33:
	mr	6, 31
	bl hddlog_write
.LBB3_34:
	addi 4, 28, 1123
	addi 3, 1, 184
	std 31, 184(1)
	bl append_str
	lwz 3, 8(15)
	cmplwi	3, 0
	beq	0, .LBB3_36
	addi 4, 28, 459
	addi 28, 1, 184
	mr	3, 28
	bl append_str
	lwz 4, 8(15)
	mr	3, 28
	bl format_dec
	b .LBB3_37
.LBB3_36:
	addi 4, 28, 542
	addi 3, 1, 184
	bl append_str
	li 3, 0
	stw 3, 12(15)
.LBB3_37:
	ld 3, 184(1)
	li 4, 0
	addi 6, 1, 192
	stb 4, 0(3)
	lis 3, 17742
	ori 3, 3, 17440
	ld 27, 136(1)
	lwz 4, 8(15)
	lwz 5, 0(15)
	bl hddlog_write
	lwz 3, -4(15)
	ori 3, 3, 2
	stw 3, -4(15)
.LBB3_38:
	cmplwi	27, 7
	rldic 3, 27, 6, 26
	add 3, 17, 3
	addi 28, 3, 1024
	stdx 28, 0, 31
	beq	0, .LBB3_56
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
	bne	0, .LBB3_52
	ld 30, .LC0@toc(2)
	addi 3, 1, 192
	addi 4, 30, 155
	bl append_str
	lwz 3, 8(15)
	cmplwi	3, 1
	bne	0, .LBB3_58
	addi 4, 30, 983
	b .LBB3_53
.LBB3_48:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 352
	bl append_str
	ld 4, 1744(17)
	mr	3, 27
	bl format_hex64
	addi 4, 30, 279
	mr	3, 27
	bl append_str
	ld 4, 1752(17)
	b .LBB3_57
.LBB3_49:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 363
	bl append_str
	lwa 4, 2008(17)
	mr	3, 27
	bl format_s32
	addi 4, 30, 107
	mr	3, 27
	bl append_str
	lwa 4, 2012(17)
	mr	3, 27
	bl format_s32
	addi 4, 30, 31
	mr	3, 27
	bl append_str
	lwa 4, 2020(17)
	mr	3, 27
	bl format_s32
	addi 4, 30, 36
	mr	3, 27
	bl append_str
	lwa 4, 2024(17)
	mr	3, 27
	bl format_s32
	b .LBB3_61
.LBB3_50:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 408
	bl append_str
	lwz 4, 1720(17)
	mr	3, 27
	bl format_dec
	addi 4, 30, 176
	mr	3, 27
	bl append_str
	lwz 4, 1724(17)
	mr	3, 27
	bl format_dec
	addi 4, 30, 287
	mr	3, 27
	bl append_str
	lwz 4, 1728(17)
	mr	3, 27
	b .LBB3_60
.LBB3_51:
	ld 30, .LC0@toc(2)
	addi 29, 1, 192
	mr	3, 29
	addi 4, 30, 2
	bl append_str
	lwz 4, 0(15)
	mr	3, 29
	bl format_dec
	addi 4, 30, 101
	mr	3, 29
	bl append_str
	lwz 4, 68(15)
	mr	3, 29
	bl format_dec
	addi 4, 30, 169
	mr	3, 29
	bl append_str
	lhz 4, 72(15)
	mr	3, 29
	bl format_dec
	addi 4, 30, 271
	mr	3, 29
	bl append_str
	lwz 4, 4(15)
	mr	3, 29
	bl format_hex32
	b .LBB3_61
.LBB3_52:
	ld 3, .LC0@toc(2)
	addi 4, 3, 629
.LBB3_53:
	addi 3, 1, 192
	bl append_str
	b .LBB3_61
.LBB3_54:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 570
	bl append_str
	ld 4, 1768(17)
	mr	3, 27
	bl format_hex64
	addi 4, 30, 26
	mr	3, 27
	bl append_str
	ld 4, 1776(17)
	b .LBB3_57
.LBB3_55:
	ld 3, .LC0@toc(2)
	addi 27, 1, 192
	addi 4, 3, 556
	mr	3, 27
	bl append_str
	ld 4, 1760(17)
	b .LBB3_57
.LBB3_56:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 374
	bl append_str
	ld 4, 2040(17)
	mr	3, 27
	bl format_hex64
	addi 4, 30, 385
	mr	3, 27
	bl append_str
	ld 4, 2032(17)
.LBB3_57:
	mr	3, 27
	bl format_hex64
	b .LBB3_61
.LBB3_58:
	lwz 3, 8(15)
	cmplwi	3, 0
	beq	0, .LBB3_63
	addi 29, 1, 192
	addi 4, 30, 396
	mr	3, 29
	bl append_str
	lwz 4, 8(15)
	mr	3, 29
	bl format_dec
	addi 4, 30, 21
	mr	3, 29
	bl append_str
	lwz 4, 12(15)
	mr	3, 29
.LBB3_60:
	bl format_dec
.LBB3_61:
	ldx 3, 0, 31
	li 4, 0
	stb 4, 0(3)
.LBB3_62:
	mr	3, 28
	ld 31, 584(1)
	ld 30, 576(1)
	ld 29, 568(1)
	ld 28, 560(1)
	ld 27, 552(1)
	ld 26, 544(1)
	ld 25, 536(1)
	ld 24, 528(1)
	ld 23, 520(1)
	ld 22, 512(1)
	ld 21, 504(1)
	ld 20, 496(1)
	ld 19, 488(1)
	ld 18, 480(1)
	ld 17, 472(1)
	ld 16, 464(1)
	ld 15, 456(1)
	ld 14, 448(1)
	addi 1, 1, 592
	ld 0, 16(1)
	mtlr 0
	blr
.LBB3_63:
	addi 4, 30, 313
	addi 3, 1, 192
	bl append_str
	lbz 3, 1736(17)
	cmplwi	3, 0
	beq	0, .LBB3_73
	cmplwi	3, 2
	beq	0, .LBB3_72
	cmplwi	3, 1
	bne	0, .LBB3_74
	addi 4, 30, 89
	b .LBB3_75
.LBB3_67:
	li 4, 0
	li 5, 0
	li 6, 0
	li 7, 0
	mr	3, 23
	li 8, 0
	li 30, 0
	bl setup_atapi_block
	addi 21, 1, 184
	addi 4, 28, 898
	std 31, 184(1)
	mr	3, 21
	bl append_str
	mr	3, 21
	mr	4, 24
	bl format_hex64
	ld 3, 184(1)
	mr	4, 24
	li 5, 0
	mr	6, 31
	stb 30, 0(3)
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
	mr	19, 3
	lwz 3, 0(15)
	cmpldi	19, 0
	addi 3, 3, 1
	stw 3, 0(15)
	stw 19, 1628(17)
	beq	0, .LBB3_82
	lwz 3, 8(15)
	cmplwi	3, 0
	bne	0, .LBB3_70
	li 3, 5
	stw 3, 8(15)
.LBB3_70:
	lwz 3, 12(15)
	cmplwi	3, 0
	bne	0, .LBB3_84
	stw 19, 12(15)
	b .LBB3_84
.LBB3_72:
	addi 4, 30, 255
	b .LBB3_75
.LBB3_73:
	addi 4, 30, 342
	b .LBB3_75
.LBB3_74:
	addi 4, 30, 95
.LBB3_75:
	addi 27, 1, 192
	mr	3, 27
	bl append_str
	lbz 3, 1736(17)
	cmplwi	3, 2
	bne	0, .LBB3_61
	addi 4, 30, 162
	mr	3, 27
	bl append_str
	ldx 4, 0, 27
	li 3, 6
	addi 5, 17, 1974
	mtctr 3
	addi 3, 4, -1
.LBB3_77:
	addi 4, 3, 1
	bdz .LBB3_81
	lbz 6, 1(5)
	addi 5, 5, 1
	addi 7, 6, -32
	clrlwi	7, 7, 24
	cmplwi	7, 95
	blt	0, .LBB3_80
	li 6, 46
.LBB3_80:
	stb 6, 1(3)
	mr	3, 4
	b .LBB3_77
.LBB3_81:
	stdx 4, 0, 27
	b .LBB3_61
.LBB3_82:
	ld 4, 76(15)
	addi 5, 17, 1792
	addi 6, 17, 1680
	addi 7, 17, 1856
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_84
	lwz 3, 4(15)
	addi 4, 28, 1496
	ori 3, 3, 1
	stw 3, 4(15)
	li 3, 5
	stw 3, 8(15)
	addi 3, 1, 184
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 0
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 1680(17)
	ld 5, 1856(17)
	b .LBB3_33
.LBB3_84:
	mr	29, 17
	addi 17, 1, 184
	std 31, 184(1)
	addi 4, 28, 486
	mr	3, 17
	ori 21, 23, 4096
	ori 20, 24, 4096
	bl append_str
	clrldi	4, 19, 32
	mr	3, 17
	bl format_dec
	addi 18, 28, 322
	mr	3, 17
	mr	4, 18
	bl append_str
	ld 4, 1792(29)
	mr	3, 17
	bl format_hex64
	addi 4, 28, 191
	mr	3, 17
	bl append_str
	lwz 4, 1680(29)
	mr	3, 17
	bl format_dec
	addi 4, 28, 199
	mr	3, 17
	bl append_str
	ld 4, 1856(29)
	mr	3, 17
	bl format_hex64
	ld 3, 184(1)
	li 30, 0
	mr	4, 19
	mr	6, 31
	stb 30, 0(3)
	mr	3, 26
	ld 5, 1792(29)
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
	addi 4, 28, 919
	mr	3, 17
	std 31, 184(1)
	bl append_str
	mr	3, 17
	mr	4, 24
	bl format_hex64
	addi 19, 28, 446
	mr	3, 17
	mr	4, 19
	bl append_str
	mr	3, 17
	mr	4, 20
	bl format_hex64
	ld 3, 184(1)
	mr	4, 24
	mr	5, 20
	mr	6, 31
	stb 30, 0(3)
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
	mr	17, 3
	lwz 3, 0(15)
	cmpldi	17, 0
	addi 3, 3, 1
	stw 3, 0(15)
	stw 17, 1632(29)
	beq	0, .LBB3_89
	lwz 3, 8(15)
	cmplwi	3, 0
	bne	0, .LBB3_87
	li 3, 6
	stw 3, 8(15)
.LBB3_87:
	lwz 3, 12(15)
	cmplwi	3, 0
	bne	0, .LBB3_93
	stw 17, 12(15)
	b .LBB3_93
.LBB3_89:
	ld 4, 76(15)
	addi 5, 29, 1800
	addi 6, 29, 1684
	addi 7, 29, 1864
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_91
	lwz 3, 4(15)
	addi 4, 28, 1539
	ori 3, 3, 2
	stw 3, 4(15)
	li 3, 6
	stw 3, 8(15)
	addi 3, 1, 184
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 0
	stb 4, 0(3)
	lwz 4, 1684(29)
	ld 5, 1864(29)
	b .LBB3_100
.LBB3_91:
	li 3, 37
	addi 4, 29, 1919
	mtctr 3
	li 3, 0
	bdz .LBB3_93
.LBB3_92:
	lbzx 5, 21, 3
	addi 6, 4, 1
	addi 3, 3, 1
	stb 5, 1(4)
	mr	4, 6
	bdnz .LBB3_92
.LBB3_93:
	addi 16, 1, 184
	addi 4, 28, 500
	std 31, 184(1)
	mr	3, 16
	bl append_str
	clrldi	4, 17, 32
	mr	3, 16
	bl format_dec
	mr	3, 16
	mr	4, 18
	bl append_str
	ld 29, 144(1)
	mr	3, 16
	ld 4, 1800(29)
	bl format_hex64
	addi 4, 28, 207
	mr	3, 16
	bl append_str
	addi 4, 21, 8
	mr	3, 16
	li 5, 16
	bl format_ascii
	mr	3, 16
	mr	4, 28
	bl append_str
	ld 3, 184(1)
	li 30, 0
	mr	4, 17
	mr	6, 31
	stb 30, 0(3)
	mr	3, 26
	ld 5, 1800(29)
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
	addi 4, 28, 940
	mr	3, 16
	std 31, 184(1)
	bl append_str
	mr	3, 16
	mr	4, 24
	bl format_hex64
	mr	3, 16
	mr	4, 19
	bl append_str
	mr	3, 16
	mr	4, 20
	bl format_hex64
	ld 3, 184(1)
	mr	4, 24
	mr	5, 20
	mr	6, 31
	stb 30, 0(3)
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
	mr	17, 3
	lwz 3, 0(15)
	cmpldi	17, 0
	addi 3, 3, 1
	stw 3, 0(15)
	stw 17, 1636(29)
	beq	0, .LBB3_98
	lwz 3, 8(15)
	cmplwi	3, 0
	bne	0, .LBB3_96
	li 3, 7
	stw 3, 8(15)
.LBB3_96:
	lwz 3, 12(15)
	cmplwi	3, 0
	bne	0, .LBB3_102
	stw 17, 12(15)
	b .LBB3_102
.LBB3_98:
	ld 4, 76(15)
	addi 5, 29, 1808
	addi 6, 29, 1688
	addi 7, 29, 1872
	mr	3, 27
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB3_101
	lwz 3, 4(15)
	addi 4, 28, 1582
	ori 3, 3, 4
	stw 3, 4(15)
	li 3, 7
	stw 3, 8(15)
	addi 3, 1, 184
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 0
	stb 4, 0(3)
	lwz 4, 1688(29)
	ld 5, 1872(29)
.LBB3_100:
	lis 3, 21581
	mr	6, 31
	ori 3, 3, 20256
	bl hddlog_write
	mr	17, 29
	b .LBB3_34
.LBB3_101:
	lbz 3, 0(21)
	lbz 4, 1(21)
	lbz 5, 2(21)
	lbz 6, 3(21)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1712(29)
	lbz 3, 4(21)
	lbz 4, 5(21)
	lbz 5, 6(21)
	lbz 6, 7(21)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1716(29)
.LBB3_102:
	addi 19, 1, 184
	addi 4, 28, 514
	std 31, 184(1)
	mr	3, 19
	bl append_str
	clrldi	4, 17, 32
	mr	3, 19
	bl format_dec
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 30, 144(1)
	mr	3, 19
	ld 4, 1808(30)
	bl format_hex64
	addi 4, 28, 215
	mr	3, 19
	bl append_str
	lwz 4, 1712(30)
	mr	3, 19
	bl format_hex32
	addi 4, 28, 47
	mr	3, 19
	bl append_str
	lwz 4, 1716(30)
	mr	3, 19
	bl format_dec
	ld 3, 184(1)
	li 16, 0
	mr	4, 17
	mr	6, 31
	stb 16, 0(3)
	mr	3, 26
	ld 5, 1808(30)
	bl hddlog_write
	addi 4, 28, 1234
	mr	3, 19
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 2
	li 5, 3
	mr	6, 31
	stb 16, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 165
	li 4, 2
	li 5, 3
	li 6, 0
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 761
	stw 3, 2008(30)
	ld 3, 76(15)
	std 3, 2032(30)
	mr	3, 19
	std 31, 184(1)
	bl append_str
	extsw 4, 17
	mr	3, 19
	bl format_s32
	addi 18, 28, 223
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 4, 2032(30)
	mr	3, 19
	bl format_hex64
	ld 3, 184(1)
	mr	4, 17
	mr	6, 31
	stb 16, 0(3)
	mr	3, 26
	ld 5, 2032(30)
	bl hddlog_write
	addi 4, 28, 1293
	mr	3, 19
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 10
	li 5, 3
	mr	6, 31
	stb 16, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 165
	li 4, 10
	li 5, 3
	li 6, 0
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 878
	stw 3, 2012(30)
	ld 3, 76(15)
	std 3, 2040(30)
	mr	3, 19
	std 31, 184(1)
	bl append_str
	extsw 4, 17
	mr	3, 19
	bl format_s32
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 4, 2040(30)
	mr	3, 19
	bl format_hex64
	ld 3, 184(1)
	mr	4, 17
	mr	6, 31
	stb 16, 0(3)
	mr	3, 26
	ld 5, 2040(30)
	bl hddlog_write
	addi 4, 28, 1388
	mr	3, 19
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 10
	li 5, 0
	mr	6, 31
	stb 16, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 165
	li 4, 10
	li 5, 0
	li 6, 0
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 1005
	stw 3, 2016(30)
	ld 3, 76(15)
	std 3, 2048(30)
	mr	3, 19
	std 31, 184(1)
	bl append_str
	extsw 4, 17
	mr	3, 19
	bl format_s32
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 4, 2048(30)
	mr	3, 19
	bl format_hex64
	ld 3, 184(1)
	mr	4, 17
	mr	6, 31
	stb 16, 0(3)
	mr	3, 26
	ld 5, 2048(30)
	bl hddlog_write
	addi 4, 28, 1178
	mr	3, 19
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 10
	li 5, 0
	mr	6, 31
	stb 16, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 162
	li 4, 10
	li 6, 0
	li 7, 0
	mr	5, 20
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 780
	stw 3, 2020(30)
	ld 3, 76(15)
	std 3, 2056(30)
	mr	3, 19
	std 31, 184(1)
	bl append_str
	extsw 4, 17
	mr	3, 19
	bl format_s32
	addi 18, 28, 231
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 3, 2056(30)
	clrldi	4, 3, 32
	mr	3, 19
	bl format_dec
	ld 3, 184(1)
	mr	4, 17
	mr	6, 31
	stb 16, 0(3)
	mr	3, 26
	ld 5, 2056(30)
	bl hddlog_write
	addi 4, 28, 1206
	mr	3, 19
	std 31, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 10
	li 5, 0
	mr	6, 31
	stb 16, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 163
	li 4, 10
	li 6, 0
	li 7, 0
	mr	5, 20
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(15)
	mr	17, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 799
	stw 3, 2024(30)
	ld 3, 76(15)
	std 3, 2064(30)
	mr	3, 19
	std 31, 184(1)
	bl append_str
	extsw 4, 17
	mr	3, 19
	bl format_s32
	mr	3, 19
	mr	4, 18
	bl append_str
	ld 3, 2064(30)
	clrldi	4, 3, 32
	mr	3, 19
	bl format_dec
	ld 3, 184(1)
	mr	4, 17
	mr	6, 31
	mr	17, 30
	stb 16, 0(3)
	mr	3, 26
	ld 5, 2064(30)
	bl hddlog_write
	addi 3, 30, 1640
	addi 4, 30, 1816
	std 30, 64(1)
	addi 5, 30, 1692
	addi 6, 30, 1880
	std 6, 96(1)
	addi 7, 30, 1720
	addi 8, 30, 1736
	std 8, 112(1)
	addi 10, 28, 113
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
	mtctr 3
	addi 3, 17, 1973
	bdz .LBB3_105
.LBB3_104:
	lbzx 4, 21, 16
	addi 5, 3, 1
	addi 16, 16, 1
	stb 4, 1(3)
	mr	3, 5
	bdnz .LBB3_104
.LBB3_105:
	addi 3, 17, 1644
	addi 4, 17, 1824
	std 17, 64(1)
	addi 5, 17, 1696
	addi 6, 17, 1888
	std 6, 96(1)
	addi 7, 17, 1724
	addi 8, 17, 1737
	std 8, 112(1)
	addi 10, 28, 53
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
	addi 3, 17, 1648
	addi 4, 17, 1832
	std 17, 64(1)
	addi 5, 17, 1700
	addi 6, 17, 1896
	std 6, 96(1)
	addi 7, 17, 1728
	addi 8, 17, 1738
	std 8, 112(1)
	addi 10, 28, 120
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
	addi 3, 17, 1840
	addi 4, 17, 1704
	std 17, 64(1)
	addi 5, 17, 1904
	addi 6, 17, 1732
	std 6, 104(1)
	addi 7, 17, 1739
	addi 11, 17, 1652
	std 7, 112(1)
	addi 10, 28, 127
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
	addi 24, 1, 184
	addi 4, 28, 743
	std 31, 184(1)
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	addi 4, 28, 528
	mr	3, 24
	bl append_str
	ld 3, 184(1)
	li 30, 0
	mr	4, 22
	lis 5, 16
	mr	6, 31
	stb 30, 0(3)
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
	lwz 4, 0(15)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(15)
	addi 4, 28, 644
	stw 3, 1616(17)
	mr	3, 24
	std 31, 184(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 23
	li 5, 0
	mr	6, 31
	stb 30, 0(3)
	mr	3, 26
	bl hddlog_write
	b .LBB3_31
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
	lbz 7, 726(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB8_1
	.long	0
	.quad	0
.Lfunc_end8:
	.size	format_hex64, .Lfunc_end8-.Lfunc_begin8

	.p2align	2
	.type	setup_atapi_block,@function
setup_atapi_block:
.Lfunc_begin9:
	li 9, 9
	addi 10, 3, -8
	mtctr 9
	li 9, 0
	bdz .LBB9_2
.LBB9_1:
	addi 11, 10, 8
	std 9, 8(10)
	mr	10, 11
	bdnz .LBB9_1
.LBB9_2:
	cmplwi	4, 3
	stb 4, 0(3)
	beq	0, .LBB9_4
	cmplwi	4, 18
	bne	0, .LBB9_5
.LBB9_4:
	stb 5, 4(3)
.LBB9_5:
	li 4, 12
	stw 4, 32(3)
	li 4, 1
	stw 5, 36(3)
	stw 4, 40(3)
	stw 6, 44(3)
	stw 7, 48(3)
	std 8, 56(3)
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
	ld 6, .LC0@toc(2)
	li 5, 9
	mtctr 5
	li 5, 28
.LBB13_1:
	bdzlr
	srw 7, 4, 5
	ld 8, 0(3)
	addi 5, 5, -4
	clrlwi	7, 7, 28
	add 7, 6, 7
	lbz 7, 726(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB13_1
	.long	0
	.quad	0
.Lfunc_end13:
	.size	format_hex32, .Lfunc_end13-.Lfunc_begin13

	.p2align	2
	.type	format_s32,@function
format_s32:
.Lfunc_begin14:
.Lfunc_gep14:
	addis 2, 12, .TOC.-.Lfunc_gep14@ha
	addi 2, 2, .TOC.-.Lfunc_gep14@l
.Lfunc_lep14:
	.localentry	format_s32, .Lfunc_lep14-.Lfunc_gep14
	cmpwi	4, 0
	bge 0, .LBB14_2
	ld 5, 0(3)
	neg 4, 4
	addi 6, 5, 1
	std 6, 0(3)
	li 6, 45
	stb 6, 0(5)
.LBB14_2:
	clrldi	4, 4, 32
	b format_dec
	#TC_RETURNd8 format_dec 0
	.long	0
	.quad	0
.Lfunc_end14:
	.size	format_s32, .Lfunc_end14-.Lfunc_begin14

	.p2align	2
	.type	execute_read_test,@function
execute_read_test:
.Lfunc_begin15:
.Lfunc_gep15:
	addis 2, 12, .TOC.-.Lfunc_gep15@ha
	addi 2, 2, .TOC.-.Lfunc_gep15@l
.Lfunc_lep15:
	.localentry	execute_read_test, .Lfunc_lep15-.Lfunc_gep15
	mfocrf 12, 32
	stw 12, 8(1)
	mflr 0
	stdu 1, -496(1)
	std 0, 512(1)
	std 24, 432(1)
	mr	24, 3
	ld 3, 608(1)
	std 3, 80(1)
	ld 3, 600(1)
	std 3, 72(1)
	ld 3, 592(1)
	std 27, 456(1)
	std 3, 48(1)
	ld 3, 560(1)
	ld 27, 544(1)
	std 14, 352(1)
	mr	14, 4
	li 4, 2048
	std 16, 368(1)
	mr	16, 5
	li 5, 165
	std 3, 64(1)
	mr	3, 27
	std 15, 360(1)
	mr	15, 7
	std 17, 376(1)
	std 18, 384(1)
	std 19, 392(1)
	std 20, 400(1)
	std 21, 408(1)
	mr	21, 6
	std 22, 416(1)
	mr	22, 10
	std 23, 424(1)
	std 25, 440(1)
	std 26, 448(1)
	std 28, 464(1)
	std 29, 472(1)
	std 30, 480(1)
	std 31, 488(1)
	std 9, 40(1)
	std 8, 56(1)
	ld 23, 584(1)
	ld 19, 576(1)
	ld 17, 568(1)
	ld 28, 552(1)
	ld 26, 536(1)
	ld 25, 528(1)
	bl prefill_buffer
	li 3, 9
	addi 4, 25, -8
	mtctr 3
	li 3, 0
	bdz .LBB15_2
.LBB15_1:
	addi 5, 4, 8
	std 3, 8(4)
	mr	4, 5
	bdnz .LBB15_1
.LBB15_2:
	li 3, 40
	ld 29, .LC0@toc(2)
	li 18, 0
	stb 3, 0(25)
	li 3, 1
	li 4, 12
	stb 18, 1(25)
	addi 31, 1, 88
	addi 20, 1, 96
	stb 18, 2(25)
	stb 18, 3(25)
	stb 18, 4(25)
	stb 14, 5(25)
	stb 18, 6(25)
	stb 18, 7(25)
	stb 3, 8(25)
	stb 18, 9(25)
	stb 18, 10(25)
	stb 18, 11(25)
	stw 4, 32(25)
	addi 4, 29, 6
	stw 16, 36(25)
	stw 21, 40(25)
	stw 15, 44(25)
	stw 3, 48(25)
	lis 3, 147
	ori 30, 3, 3884
	mr	3, 31
	std 28, 56(25)
	std 20, 88(1)
	bl append_str
	mr	3, 31
	mr	4, 22
	bl append_str
	addi 4, 29, 134
	mr	3, 31
	bl append_str
	mr	3, 31
	mr	4, 14
	bl format_dec
	addi 4, 29, 239
	mr	3, 31
	bl append_str
	mr	3, 31
	mr	4, 15
	bl format_dec
	addi 4, 29, 141
	mr	3, 31
	bl append_str
	mr	3, 31
	mr	4, 16
	bl format_dec
	addi 4, 29, 59
	mr	3, 31
	bl append_str
	mr	3, 31
	mr	4, 21
	bl format_dec
	ld 3, 88(1)
	mr	4, 26
	mr	5, 28
	mr	6, 20
	stb 18, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	mr	18, 24
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 24
	mr	6, 26
	li 7, 64
	mr	8, 28
	li 9, 2048
	bl lv1_hcall
	nop
	mr	21, 3
	lwz 3, -8(30)
	cmpldi	21, 0
	addi 3, 3, 1
	stw 3, -8(30)
	stw 21, 0(17)
	beq	0, .LBB15_7
	lwz 3, 0(30)
	mr	24, 19
	mr	17, 23
	cmplwi	3, 0
	bne	0, .LBB15_5
	ld 3, 56(1)
	stw 3, 0(30)
.LBB15_5:
	lwz 3, 4(30)
	cmplwi	3, 0
	bne	0, .LBB15_9
	stw 21, 4(30)
	b .LBB15_9
.LBB15_7:
	ld 4, 68(30)
	mr	17, 23
	mr	6, 23
	mr	3, 18
	mr	5, 19
	ld 23, 48(1)
	mr	24, 19
	mr	7, 23
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB15_9
	lwz 3, -4(30)
	ld 4, 40(1)
	or 3, 3, 4
	addi 4, 29, 332
	stw 3, -4(30)
	ld 3, 56(1)
	stw 3, 0(30)
	addi 30, 1, 88
	mr	3, 30
	std 20, 88(1)
	bl append_str
	mr	3, 30
	mr	4, 22
	bl append_str
	addi 4, 29, 1324
	mr	3, 30
	bl append_str
	ld 3, 88(1)
	li 4, 0
	mr	6, 20
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 0(17)
	ld 5, 0(23)
	bl hddlog_write
	li 3, 1
	b .LBB15_31
.LBB15_9:
	li 3, 2049
	cmpdi 2, 21, 0
	li 19, 0
	mtctr 3
	addi 3, 27, -1
	bdz .LBB15_11
.LBB15_10:
	lbz 4, 1(3)
	addi 3, 3, 1
	xori 4, 4, 165
	cntlzw	4, 4
	srwi 4, 4, 5
	add 19, 19, 4
	bdnz .LBB15_10
.LBB15_11:
	cmplwi	19, 2048
	ld 3, 72(1)
	li 30, 0
	stw 19, 0(3)
	beq	0, .LBB15_21
	lbz 3, 1(27)
	cmplwi	3, 67
	bne	0, .LBB15_17
	lbz 3, 2(27)
	cmplwi	3, 68
	bne	0, .LBB15_17
	lbz 3, 3(27)
	cmplwi	3, 48
	bne	0, .LBB15_17
	lbz 3, 4(27)
	cmplwi	3, 48
	bne	0, .LBB15_17
	lbz 3, 5(27)
	li 30, 2
	cmplwi	3, 49
	beq	0, .LBB15_21
.LBB15_17:
	li 3, 2049
	addi 4, 27, -1
	mtctr 3
	li 3, 0
	bdz .LBB15_19
.LBB15_18:
	lbz 5, 1(4)
	addi 4, 4, 1
	cntlzw	5, 5
	srwi 5, 5, 5
	add 3, 3, 5
	bdnz .LBB15_18
.LBB15_19:
	cmplwi	3, 2048
	li 30, 1
	beq	0, .LBB15_21
	li 30, 3
.LBB15_21:
	ld 3, 80(1)
	addi 4, 29, 65
	stb 30, 0(3)
	std 20, 88(1)
	addi 20, 1, 88
	mr	3, 20
	bl append_str
	mr	3, 20
	mr	4, 22
	bl append_str
	addi 4, 29, 71
	mr	3, 20
	bl append_str
	clrldi	4, 21, 32
	mr	3, 20
	bl format_dec
	addi 4, 29, 322
	mr	3, 20
	bl append_str
	ld 4, 0(24)
	mr	3, 20
	bl format_hex64
	addi 4, 29, 77
	mr	3, 20
	bl append_str
	cmplwi	30, 0
	beq	0, .LBB15_26
	cmplwi	30, 3
	beq	0, .LBB15_25
	cmplwi	30, 2
	bne	0, .LBB15_27
	addi 4, 29, 255
	b .LBB15_28
.LBB15_25:
	addi 4, 29, 95
	b .LBB15_28
.LBB15_26:
	addi 4, 29, 342
	b .LBB15_28
.LBB15_27:
	addi 4, 29, 89
.LBB15_28:
	addi 22, 1, 88
	mr	3, 22
	bl append_str
	addi 4, 29, 11
	mr	3, 22
	bl append_str
	clrldi	4, 19, 32
	mr	3, 22
	bl format_dec
	addi 4, 29, 191
	mr	3, 22
	bl append_str
	lwz 4, 0(17)
	mr	3, 22
	bl format_dec
	addi 4, 29, 16
	mr	3, 22
	bl append_str
	mr	3, 22
	mr	4, 27
	bl format_bytes_hex
	addi 4, 29, 83
	mr	3, 22
	bl append_str
	addi 4, 27, 16
	mr	3, 22
	bl format_bytes_hex
	addi 4, 29, 148
	mr	3, 22
	bl append_str
	addi 4, 27, 40
	mr	3, 22
	li 5, 8
	bl format_ascii
	addi 4, 29, 247
	mr	3, 22
	bl append_str
	addi 4, 27, 2032
	mr	3, 22
	bl format_bytes_hex
	ld 3, 88(1)
	li 4, 0
	addi 6, 1, 96
	stb 4, 0(3)
	lis 3, 20559
	mr	4, 21
	ori 3, 3, 21332
	ld 5, 0(24)
	bl hddlog_write
	bc 4, 10, .LBB15_30
	ld 3, 0(24)
	clrldi	3, 3, 56
	cmpldi	3, 2
	li 3, 0
	bne	0, .LBB15_31
.LBB15_30:
	ld 8, 64(1)
	mr	3, 18
	mr	4, 25
	mr	5, 26
	mr	6, 27
	mr	7, 28
	bl do_request_sense
	li 3, -1
.LBB15_31:
	ld 31, 488(1)
	ld 30, 480(1)
	ld 29, 472(1)
	ld 28, 464(1)
	ld 27, 456(1)
	ld 26, 448(1)
	ld 25, 440(1)
	ld 24, 432(1)
	ld 23, 424(1)
	ld 22, 416(1)
	ld 21, 408(1)
	ld 20, 400(1)
	ld 19, 392(1)
	ld 18, 384(1)
	ld 17, 376(1)
	ld 16, 368(1)
	ld 15, 360(1)
	ld 14, 352(1)
	addi 1, 1, 496
	ld 0, 16(1)
	lwz 12, 8(1)
	mtlr 0
	mtocrf 32, 12
	blr
	.long	0
	.quad	0
.Lfunc_end15:
	.size	execute_read_test, .Lfunc_end15-.Lfunc_begin15

	.p2align	2
	.type	format_bytes_hex,@function
format_bytes_hex:
.Lfunc_begin16:
.Lfunc_gep16:
	addis 2, 12, .TOC.-.Lfunc_gep16@ha
	addi 2, 2, .TOC.-.Lfunc_gep16@l
.Lfunc_lep16:
	.localentry	format_bytes_hex, .Lfunc_lep16-.Lfunc_gep16
	ld 6, .LC0@toc(2)
	li 5, 17
	mtctr 5
	addi 5, 4, -1
	addi 4, 6, 726
.LBB16_1:
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
	b .LBB16_1
	.long	0
	.quad	0
.Lfunc_end16:
	.size	format_bytes_hex, .Lfunc_end16-.Lfunc_begin16

	.p2align	2
	.type	do_request_sense,@function
do_request_sense:
.Lfunc_begin17:
.Lfunc_gep17:
	addis 2, 12, .TOC.-.Lfunc_gep17@ha
	addi 2, 2, .TOC.-.Lfunc_gep17@l
.Lfunc_lep17:
	.localentry	do_request_sense, .Lfunc_lep17-.Lfunc_gep17
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
	addi 4, 22, 1051
	bl append_str
	mr	3, 24
	mr	4, 25
	bl format_hex64
	addi 4, 22, 446
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
	beq	0, .LBB17_2
.LBB17_1:
	addi 27, 1, 32
	addi 4, 22, 676
	std 29, 32(1)
	mr	3, 27
	bl append_str
	clrldi	4, 28, 32
	mr	3, 27
	bl format_dec
	addi 4, 22, 322
	mr	3, 27
	bl append_str
	ld 4, 1848(30)
	mr	3, 27
	bl format_hex64
	addi 4, 22, 295
	mr	3, 27
	bl append_str
	lbz 3, 1958(30)
	clrldi	4, 3, 60
	mr	3, 27
	bl format_hex32
	addi 4, 22, 263
	mr	3, 27
	bl append_str
	lbz 4, 1968(30)
	mr	3, 27
	bl format_hex32
	addi 4, 22, 304
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
	b .LBB17_4
.LBB17_2:
	ori 25, 21, 3876
	addi 5, 30, 1848
	ld 4, 76(25)
	addi 6, 30, 1708
	addi 7, 30, 1912
	mr	3, 26
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB17_5
	lwz 3, 4(25)
	addi 4, 22, 1098
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
.LBB17_4:
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
.LBB17_5:
	li 3, 19
	addi 4, 27, -1
	mtctr 3
	addi 5, 30, 1955
	li 3, 0
	bdz .LBB17_1
.LBB17_6:
	lbz 6, 1(4)
	addi 7, 5, 1
	addi 4, 4, 1
	addi 3, 3, 1
	stb 6, 1(5)
	mr	5, 7
	bdnz .LBB17_6
	b .LBB17_1
	.long	0
	.quad	0
.Lfunc_end17:
	.size	do_request_sense, .Lfunc_end17-.Lfunc_begin17

	.type	.L_MergedGlobals,@object
	.section	.rodata,"a",@progbits
.L_MergedGlobals:
	.asciz	"'"
	.asciz	"HC="
	.asciz	"pre "
	.asciz	" a5="
	.asciz	" w0="
	.asciz	" RC="
	.asciz	" SZ="
	.asciz	" R0="
	.asciz	" W0="
	.asciz	" hdd="
	.asciz	" blk="
	.asciz	"pio_0"
	.asciz	" bsz="
	.asciz	"post "
	.asciz	": rc="
	.asciz	" cls="
	.asciz	" w16="
	.asciz	"ZEROS"
	.asciz	"OTHER"
	.asciz	" LOG="
	.asciz	" P10="
	.asciz	"pio_16"
	.asciz	"pio_17"
	.asciz	"dma_16"
	.asciz	": lba="
	.asciz	" blks="
	.asciz	" vol='"
	.asciz	"P10-V1"
	.asciz	" PVD: "
	.asciz	" SKIP="
	.asciz	" 0_A5="
	.asciz	" rgn=0x"
	.asciz	" polls="
	.asciz	" ticks="
	.asciz	" resp='"
	.asciz	" lba=0x"
	.asciz	" val=0x"
	.asciz	" bytes="
	.asciz	" proto="
	.asciz	"' wend="
	.asciz	"DATA_OK"
	.asciz	" asc=0x"
	.asciz	" TMO=0x"
	.asciz	" BUS=0x"
	.asciz	" 17_A5="
	.asciz	" skey=0x"
	.asciz	" ascq=0x"
	.asciz	" PIO16: "
	.asciz	" async=0x"
	.asciz	"timeout: "
	.asciz	"UNCHANGED"
	.asciz	"DMA RGN=0x"
	.asciz	"VUART: P2="
	.asciz	"P10_VAL=0x"
	.asciz	" P2_VAL=0x"
	.asciz	" FAIL STEP="
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
	.asciz	"CDVD LPAR: 0x"
	.asciz	"CDVD EA:   0x"
	.asciz	"scan: rom_cnt="
	.asciz	"post open: rc="
	.asciz	"post free: rc="
	.asciz	"P10-V1 RUNNING"
	.asciz	"post unmap: rc="
	.asciz	"post close: rc="
	.asciz	"post sense: rc="
	.asciz	"pre map: lpar=0x"
	.asciz	"pre free: rgn=0x"
	.asciz	"0123456789abcdef"
	.asciz	"pre unmap: rgn=0x"
	.asciz	"post vuart_p2: rc="
	.asciz	"post vuart_r0: rc="
	.asciz	"post vuart_w0: rc="
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"post dma_alloc: rc="
	.asciz	"post vuart_p10: rc="
	.asciz	"pre tur: cmd_lpar=0x"
	.asciz	"pre inq: cmd_lpar=0x"
	.asciz	"pre cap: cmd_lpar=0x"
	.asciz	"pre open: bus=4 dev=2"
	.asciz	" SANITY REJECT (0 HC)"
	.asciz	"post vuart_p10_p0: rc="
	.asciz	"pre close: bus=4 dev=2"
	.asciz	"pre sense: cmd_lpar=0x"
	.asciz	"boot: ps2_netemu_p10_V1"
	.asciz	"timeout: sense timed out"
	.asciz	"finish: ps2_netemu_p10_V1 "
	.asciz	"post dma_alloc: rc=0 rgn=0x"
	.asciz	"pre vuart_r0: port=10 len=0"
	.asciz	"pre vuart_w0: port=10 len=0"
	.asciz	"pre vuart_p2: port=2 param=3"
	.asciz	"grd ok: lpar & ea sanity pass"
	.asciz	"pre vuart_p10: port=10 param=3"
	.asciz	" timed out; halting hypercalls"
	.asciz	"grd reject: sanity failed (0 hc)"
	.asciz	"pre vuart_p10_p0: port=10 param=0"
	.asciz	"pre dma_alloc: sz=0x100000 pexp=20"
	.asciz	"finish: ps2_netemu_p9_U1 failed step=1"
	.asciz	"timeout: tur timed out; halting hypercalls"
	.asciz	"timeout: inq timed out; halting hypercalls"
	.asciz	"timeout: cap timed out; halting hypercalls"
	.size	.L_MergedGlobals, 1625

.L.str.27 = .L_MergedGlobals
	.size	.L.str.27, 2
.L.str.90 = .L_MergedGlobals+2
	.size	.L.str.90, 4
.L.str.59 = .L_MergedGlobals+6
	.size	.L.str.59, 5
.L.str.69 = .L_MergedGlobals+11
	.size	.L.str.69, 5
.L.str.70 = .L_MergedGlobals+16
	.size	.L.str.70, 5
.L.str.89 = .L_MergedGlobals+21
	.size	.L.str.89, 5
.L.str.96 = .L_MergedGlobals+26
	.size	.L.str.96, 5
.L.str.104 = .L_MergedGlobals+31
	.size	.L.str.104, 5
.L.str.105 = .L_MergedGlobals+36
	.size	.L.str.105, 5
.L.str.2 = .L_MergedGlobals+41
	.size	.L.str.2, 6
.L.str.32 = .L_MergedGlobals+47
	.size	.L.str.32, 6
.L.str.46 = .L_MergedGlobals+53
	.size	.L.str.46, 6
.L.str.63 = .L_MergedGlobals+59
	.size	.L.str.63, 6
.L.str.66 = .L_MergedGlobals+65
	.size	.L.str.66, 6
.L.str.67 = .L_MergedGlobals+71
	.size	.L.str.67, 6
.L.str.68 = .L_MergedGlobals+77
	.size	.L.str.68, 6
.L.str.71 = .L_MergedGlobals+83
	.size	.L.str.71, 6
.L.str.75 = .L_MergedGlobals+89
	.size	.L.str.75, 6
.L.str.77 = .L_MergedGlobals+95
	.size	.L.str.77, 6
.L.str.91 = .L_MergedGlobals+101
	.size	.L.str.91, 6
.L.str.103 = .L_MergedGlobals+107
	.size	.L.str.103, 6
.L.str.45 = .L_MergedGlobals+113
	.size	.L.str.45, 7
.L.str.47 = .L_MergedGlobals+120
	.size	.L.str.47, 7
.L.str.48 = .L_MergedGlobals+127
	.size	.L.str.48, 7
.L.str.60 = .L_MergedGlobals+134
	.size	.L.str.60, 7
.L.str.62 = .L_MergedGlobals+141
	.size	.L.str.62, 7
.L.str.72 = .L_MergedGlobals+148
	.size	.L.str.72, 7
.L.str.84 = .L_MergedGlobals+155
	.size	.L.str.84, 7
.L.str.87 = .L_MergedGlobals+162
	.size	.L.str.87, 7
.L.str.92 = .L_MergedGlobals+169
	.size	.L.str.92, 7
.L.str.100 = .L_MergedGlobals+176
	.size	.L.str.100, 7
.L.str.13 = .L_MergedGlobals+183
	.size	.L.str.13, 8
.L.str.20 = .L_MergedGlobals+191
	.size	.L.str.20, 8
.L.str.21 = .L_MergedGlobals+199
	.size	.L.str.21, 8
.L.str.26 = .L_MergedGlobals+207
	.size	.L.str.26, 8
.L.str.31 = .L_MergedGlobals+215
	.size	.L.str.31, 8
.L.str.35 = .L_MergedGlobals+223
	.size	.L.str.35, 8
.L.str.42 = .L_MergedGlobals+231
	.size	.L.str.42, 8
.L.str.61 = .L_MergedGlobals+239
	.size	.L.str.61, 8
.L.str.73 = .L_MergedGlobals+247
	.size	.L.str.73, 8
.L.str.76 = .L_MergedGlobals+255
	.size	.L.str.76, 8
.L.str.82 = .L_MergedGlobals+263
	.size	.L.str.82, 8
.L.str.93 = .L_MergedGlobals+271
	.size	.L.str.93, 8
.L.str.98 = .L_MergedGlobals+279
	.size	.L.str.98, 8
.L.str.101 = .L_MergedGlobals+287
	.size	.L.str.101, 8
.L.str.81 = .L_MergedGlobals+295
	.size	.L.str.81, 9
.L.str.83 = .L_MergedGlobals+304
	.size	.L.str.83, 9
.L.str.86 = .L_MergedGlobals+313
	.size	.L.str.86, 9
.L.str.19 = .L_MergedGlobals+322
	.size	.L.str.19, 10
.L.str.64 = .L_MergedGlobals+332
	.size	.L.str.64, 10
.L.str.74 = .L_MergedGlobals+342
	.size	.L.str.74, 10
.L.str.97 = .L_MergedGlobals+352
	.size	.L.str.97, 11
.L.str.102 = .L_MergedGlobals+363
	.size	.L.str.102, 11
.L.str.106 = .L_MergedGlobals+374
	.size	.L.str.106, 11
.L.str.107 = .L_MergedGlobals+385
	.size	.L.str.107, 11
.L.str.88 = .L_MergedGlobals+396
	.size	.L.str.88, 12
.L.str.99 = .L_MergedGlobals+408
	.size	.L.str.99, 12
.L.str.3 = .L_MergedGlobals+420
	.size	.L.str.3, 13
.L.str.15 = .L_MergedGlobals+433
	.size	.L.str.15, 13
.L.str.23 = .L_MergedGlobals+446
	.size	.L.str.23, 13
.L.str.58 = .L_MergedGlobals+459
	.size	.L.str.58, 13
.L.str.14 = .L_MergedGlobals+472
	.size	.L.str.14, 14
.L.str.18 = .L_MergedGlobals+486
	.size	.L.str.18, 14
.L.str.25 = .L_MergedGlobals+500
	.size	.L.str.25, 14
.L.str.30 = .L_MergedGlobals+514
	.size	.L.str.30, 14
.L.str.50 = .L_MergedGlobals+528
	.size	.L.str.50, 14
.L.str.57 = .L_MergedGlobals+542
	.size	.L.str.57, 14
.L.str.94 = .L_MergedGlobals+556
	.size	.L.str.94, 14
.L.str.95 = .L_MergedGlobals+570
	.size	.L.str.95, 14
.L.str.1 = .L_MergedGlobals+584
	.size	.L.str.1, 15
.L.str.8 = .L_MergedGlobals+599
	.size	.L.str.8, 15
.L.str.53 = .L_MergedGlobals+614
	.size	.L.str.53, 15
.L.str.108 = .L_MergedGlobals+629
	.size	.L.str.108, 15
.L.str.51 = .L_MergedGlobals+644
	.size	.L.str.51, 16
.L.str.55 = .L_MergedGlobals+660
	.size	.L.str.55, 16
.L.str.80 = .L_MergedGlobals+676
	.size	.L.str.80, 16
.L.str.12 = .L_MergedGlobals+692
	.size	.L.str.12, 17
.L.str.52 = .L_MergedGlobals+709
	.size	.L.str.52, 17
.L__const.format_bytes_hex.hex = .L_MergedGlobals+726
	.size	.L__const.format_bytes_hex.hex, 17
.L.str.49 = .L_MergedGlobals+743
	.size	.L.str.49, 18
.L.str.34 = .L_MergedGlobals+761
	.size	.L.str.34, 19
.L.str.41 = .L_MergedGlobals+780
	.size	.L.str.41, 19
.L.str.44 = .L_MergedGlobals+799
	.size	.L.str.44, 19
hddlog_init.path = .L_MergedGlobals+818
	.size	hddlog_init.path, 20
hddlog_write.path = .L_MergedGlobals+838
	.size	hddlog_write.path, 20
.L.str.10 = .L_MergedGlobals+858
	.size	.L.str.10, 20
.L.str.37 = .L_MergedGlobals+878
	.size	.L.str.37, 20
.L.str.16 = .L_MergedGlobals+898
	.size	.L.str.16, 21
.L.str.22 = .L_MergedGlobals+919
	.size	.L.str.22, 21
.L.str.28 = .L_MergedGlobals+940
	.size	.L.str.28, 21
.L.str.7 = .L_MergedGlobals+961
	.size	.L.str.7, 22
.L.str.85 = .L_MergedGlobals+983
	.size	.L.str.85, 22
.L.str.39 = .L_MergedGlobals+1005
	.size	.L.str.39, 23
.L.str.54 = .L_MergedGlobals+1028
	.size	.L.str.54, 23
.L.str.78 = .L_MergedGlobals+1051
	.size	.L.str.78, 23
.L.str = .L_MergedGlobals+1074
	.size	.L.str, 24
.L.str.79 = .L_MergedGlobals+1098
	.size	.L.str.79, 25
.L.str.56 = .L_MergedGlobals+1123
	.size	.L.str.56, 27
.L.str.11 = .L_MergedGlobals+1150
	.size	.L.str.11, 28
.L.str.40 = .L_MergedGlobals+1178
	.size	.L.str.40, 28
.L.str.43 = .L_MergedGlobals+1206
	.size	.L.str.43, 28
.L.str.33 = .L_MergedGlobals+1234
	.size	.L.str.33, 29
.L.str.6 = .L_MergedGlobals+1263
	.size	.L.str.6, 30
.L.str.36 = .L_MergedGlobals+1293
	.size	.L.str.36, 31
.L.str.65 = .L_MergedGlobals+1324
	.size	.L.str.65, 31
.L.str.4 = .L_MergedGlobals+1355
	.size	.L.str.4, 33
.L.str.38 = .L_MergedGlobals+1388
	.size	.L.str.38, 34
.L.str.9 = .L_MergedGlobals+1422
	.size	.L.str.9, 35
.L.str.5 = .L_MergedGlobals+1457
	.size	.L.str.5, 39
.L.str.17 = .L_MergedGlobals+1496
	.size	.L.str.17, 43
.L.str.24 = .L_MergedGlobals+1539
	.size	.L.str.24, 43
.L.str.29 = .L_MergedGlobals+1582
	.size	.L.str.29, 43
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
