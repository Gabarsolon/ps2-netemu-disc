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
	li 3, 50
	bl wait_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB0_9
	ld 3, .LC0@toc(2)
	li 27, 0
	addi 4, 3, 827
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
	li 3, 10
	bl wait_hdd_log_safe
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
	.type	wait_hdd_log_safe,@function
wait_hdd_log_safe:
.Lfunc_begin1:
.Lfunc_gep1:
	addis 2, 12, .TOC.-.Lfunc_gep1@ha
	addi 2, 2, .TOC.-.Lfunc_gep1@l
.Lfunc_lep1:
	.localentry	wait_hdd_log_safe, .Lfunc_lep1-.Lfunc_gep1
	mflr 0
	std 27, -40(1)
	std 28, -32(1)
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -80(1)
	lis 4, 577
	addi 28, 3, 1
	std 0, 96(1)
	ori 29, 4, 51296
	lis 27, 773
.LBB1_1:
	addi 28, 28, -1
	cmpldi	28, 0
	bc 4, 1, .LBB1_9
	lbz 4, 117(29)
	lbz 3, 104(29)
	xori 4, 4, 1
	ld 5, 0(29)
	clrlwi	6, 3, 24
	or. 4, 4, 6
	cmpdi 1, 5, 3
	ld 3, 40(29)
	crand 20, 2, 6
	ld 4, 48(29)
	ld 5, 56(29)
	bc 4, 20, .LBB1_7
	cmpdi	5, 0
	bc 4, 2, .LBB1_7
	cmpdi	3, 0
	bc 4, 2, .LBB1_7
	cmpdi	4, 0
	bc 4, 2, .LBB1_7
	lwz 3, 20864(27)
	cmplwi	3, 0
	beq	0, .LBB1_10
.LBB1_7:
	bl native_clock
	nop
	mr	30, 3
.LBB1_8:
	bl native_clock
	nop
	sub	3, 3, 30
	rldicl 3, 3, 61, 3
	cmpldi	3, 9975
	blt	0, .LBB1_8
	b .LBB1_1
.LBB1_9:
	li 3, 0
	b .LBB1_11
.LBB1_10:
	li 3, 1
.LBB1_11:
	addi 1, 1, 80
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	ld 28, -32(1)
	ld 27, -40(1)
	blr
	.long	0
	.quad	0
.Lfunc_end1:
	.size	wait_hdd_log_safe, .Lfunc_end1-.Lfunc_begin1

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
	beq	0, .LBB2_28
	ldx 29, 22, 3
	lwz 3, 1668(29)
	cmplwi	3, 0
	beq	0, .LBB2_28
	lwz 3, 1672(29)
	cmplwi	3, 128
	blt	0, .LBB2_4
	li 3, 8
	b .LBB2_27
.LBB2_4:
	li 3, 50
	mr	26, 6
	mr	24, 5
	bl wait_hdd_log_safe
	cmplwi	3, 0
	beq	0, .LBB2_9
	ld 3, .LC0@toc(2)
	li 21, 0
	addi 4, 3, 847
	li 3, 0
	bl stock_ufs_open
	nop
	mr	27, 3
	cmplwi	27, 8
	blt	0, .LBB2_10
	cmpwi	27, -2
	li 3, 2
	beq	0, .LBB2_8
	li 3, 6
.LBB2_8:
	stb 3, 0(22)
	b .LBB2_28
.LBB2_9:
	lhz 3, -2(22)
	li 30, 0
	addi 3, 3, 1
	sth 3, -2(22)
	b .LBB2_28
.LBB2_10:
	li 3, 65
	addi 25, 29, 512
	mtctr 3
	li 3, 512
	bdz .LBB2_12
.LBB2_11:
	stdx 21, 29, 3
	addi 3, 3, 8
	bdnz .LBB2_11
.LBB2_12:
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
	beq	0, .LBB2_17
	addi 4, 26, -1
	addi 5, 29, 583
.LBB2_14:
	lbzu 6, 1(4)
	cmpwi	6, 0
	bc 12, 2, .LBB2_17
	cmpldi	3, 438
	bc 12, 1, .LBB2_17
	addi 7, 5, 1
	stb 6, 1(5)
	addi 3, 3, 1
	mr	5, 7
	b .LBB2_14
.LBB2_17:
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
	bne	0, .LBB2_25
	lwz 3, 1672(29)
	xoris 4, 28, 17742
	cmplwi	4, 17440
	addi 26, 3, 1
	stw 26, 28(29)
	lwz 3, -6(22)
	addi 3, 3, 1
	stw 3, 44(29)
	bne	0, .LBB2_20
	li 3, 1
	stw 3, 40(29)
	stb 3, 1(22)
.LBB2_20:
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
	bne	0, .LBB2_26
	cmplwi	3, 0
	bne	0, .LBB2_26
	stw 26, 1672(29)
	lwz 3, -6(22)
	addi 3, 3, 1
	stw 3, -6(22)
	li 3, 10
	bl wait_hdd_log_safe
	cmplwi	3, 0
	li 30, 0
	beq	0, .LBB2_28
	bl stock_hdd_cache_flush
	nop
	cmplwi	3, 0
	beq	0, .LBB2_28
	li 3, 7
	b .LBB2_27
.LBB2_25:
	mr	3, 27
	bl stock_ufs_close
	nop
.LBB2_26:
	li 3, 6
.LBB2_27:
	stb 3, 0(22)
.LBB2_28:
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
	std 16, 464(1)
	li 16, 0
	std 14, 448(1)
	std 15, 456(1)
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
	std 27, 552(1)
	std 28, 560(1)
	std 29, 568(1)
	std 30, 576(1)
	std 31, 584(1)
	bgt	0, .LBB3_2
	mr	16, 3
.LBB3_2:
	ori 17, 4, 3876
	bl get_arena
	cmpldi	3, 0
	beq	0, .LBB3_18
	mr	29, 3
.LBB3_4:
	bl native_clock
	nop
	ld 4, 60(17)
	lis 5, 1826
	cmpdi	4, 0
	std 3, 60(17)
	sub	3, 3, 4
	ori 4, 5, 31264
	bc 12, 2, .LBB3_7
	cmpld	3, 4
	bc 4, 1, .LBB3_7
	lwz 3, 16(17)
	addi 3, 3, 1
	stw 3, 16(17)
.LBB3_7:
	lwz 3, -4(17)
	addi 15, 1, 192
	andi. 3, 3, 2
	bne	0, .LBB3_38
	lis 3, 1122
	ori 3, 3, 30067
	rotldi	28, 3, 40
	bl hddlog_init
	ld 3, .LC0@toc(2)
	std 15, 184(1)
	std 3, 136(1)
	addi 4, 3, 975
	addi 3, 1, 184
	bl append_str
	ld 3, 184(1)
	li 18, 0
	li 4, 2216
	li 5, 2
	mr	6, 15
	stb 18, 0(3)
	lis 3, 16975
	li 7, 2
	ori 3, 3, 20308
	std 15, 128(1)
	std 7, 144(1)
	bl hddlog_write
	lis 3, 50
	lis 5, 29285
	lis 4, 29817
	ori 3, 3, 12987
	ori 5, 5, 26473
	ori 4, 4, 28773
	rldic 30, 3, 41, 1
	rldic 3, 5, 32, 1
	li 14, 9
	li 19, 0
	addi 26, 1, 176
	addi 25, 1, 168
	addi 24, 1, 160
	addi 23, 1, 152
	li 27, 0
	rldic 22, 4, 32, 1
	oris 21, 3, 28526
	li 15, 0
	li 31, 0
.LBB3_9:
	addi 14, 14, -1
	cmpldi	14, 0
	bc 4, 1, .LBB3_22
	add 20, 27, 30
	mr	3, 26
	std 18, 176(1)
	mr	4, 25
	mr	5, 28
	std 18, 168(1)
	mr	6, 20
	mr	7, 22
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
	addi 15, 15, 1
	cmpldi	3, 0
	beq	0, .LBB3_17
	cmpldi	3, 5
	bne	0, .LBB3_11
	mr	3, 24
	mr	4, 23
	std 18, 160(1)
	mr	5, 28
	mr	6, 20
	std 18, 152(1)
	mr	7, 21
	li 8, 0
	bl repo_read
	nop
	cmpldi	3, 0
	bne	0, .LBB3_16
	ld 3, 160(1)
	stw 3, 1660(29)
.LBB3_16:
	addi 31, 31, 1
	std 27, 144(1)
	b .LBB3_11
.LBB3_17:
	li 19, 1
	b .LBB3_11
.LBB3_18:
	lwz 3, -4(17)
	andi. 3, 3, 8
	lis 3, 48
	ori 28, 3, 20160
	bne	0, .LBB3_66
	lwz 3, -4(17)
	li 4, 3
	li 5, 0
	li 30, 0
	ori 3, 3, 1
	stw 3, -4(17)
	li 3, 4096
	bl native_alloc
	nop
	mr	29, 3
	bl arena_rw
	cmplwi	3, 0
	beq	0, .LBB3_26
	std 29, 20(17)
	lwz 3, -4(17)
	ori 3, 3, 4
	stw 3, -4(17)
	li 3, 2217
	mtctr 3
	addi 3, 29, -1
	bdz .LBB3_4
.LBB3_21:
	addi 4, 3, 1
	stb 30, 1(3)
	mr	3, 4
	bdnz .LBB3_21
	b .LBB3_4
.LBB3_22:
	stw 15, 1664(29)
	lis 3, 18258
	lis 4, 17742
	addi 26, 1, 184
	ori 21, 3, 17440
	stw 31, 36(17)
	ori 28, 4, 17440
	mr	3, 26
	stw 19, 40(17)
	ld 30, 136(1)
	ld 15, 128(1)
	addi 4, 30, 633
	std 15, 184(1)
	bl append_str
	clrldi	25, 31, 32
	mr	3, 26
	mr	4, 25
	bl format_dec
	addi 4, 30, 58
	mr	3, 26
	bl append_str
	clrldi	24, 19, 32
	mr	3, 26
	mr	4, 24
	bl format_dec
	addi 4, 30, 497
	mr	3, 26
	bl append_str
	ld 3, 184(1)
	li 22, 0
	mr	4, 25
	mr	5, 24
	mr	6, 15
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
	stw 3, 8(17)
	li 3, -1
	addi 4, 30, 1176
	stw 3, 12(17)
	mr	3, 27
	std 15, 184(1)
	bl append_str
	ld 3, 184(1)
	mr	4, 24
	mr	5, 23
	mr	6, 15
	stb 22, 0(3)
	mr	3, 21
	bl hddlog_write
	addi 4, 30, 1313
	mr	3, 27
	std 15, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 1
	li 5, 0
	mr	6, 15
	stb 22, 0(3)
	mr	3, 28
	b .LBB3_37
.LBB3_24:
	addi 26, 1, 184
	std 24, 1760(29)
	addi 4, 30, 1081
	std 23, 1768(29)
	std 3, 1776(29)
	mr	3, 26
	std 15, 184(1)
	bl append_str
	ld 3, 184(1)
	mr	4, 24
	mr	5, 23
	mr	6, 15
	stb 22, 0(3)
	mr	3, 21
	bl hddlog_write
	addi 4, 30, 908
	mr	3, 26
	std 15, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 4
	mr	6, 15
	ld 31, 144(1)
	stb 22, 0(3)
	lis 3, 20562
	mr	5, 31
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 170
	li 4, 4
	li 6, 0
	li 7, 0
	mr	5, 31
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	25, 3
	mr	3, 26
	addi 4, 4, 1
	stw 4, 0(17)
	addi 4, 30, 648
	stw 25, 1604(29)
	std 15, 184(1)
	bl append_str
	clrldi	4, 25, 32
	mr	3, 26
	bl format_dec
	ld 3, 184(1)
	mr	4, 25
	li 5, 0
	mr	6, 15
	stb 22, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	bl hddlog_write
	cmpldi	25, 0
	beq	0, .LBB3_27
	li 3, 2
	stw 3, 8(17)
	stw 25, 12(17)
	b .LBB3_33
.LBB3_26:
	lwz 3, -4(17)
	ori 3, 3, 8
	stw 3, -4(17)
	b .LBB3_66
.LBB3_27:
	lis 3, 20562
	lis 4, 20559
	std 15, 184(1)
	ori 25, 3, 17696
	ori 26, 4, 21332
	addi 4, 30, 1242
	addi 3, 1, 184
	bl append_str
	ld 3, 184(1)
	li 14, 0
	lis 4, 16
	li 5, 20
	mr	6, 15
	stb 14, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 174
	li 4, 4
	lis 6, 16
	li 7, 20
	mr	5, 31
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	mr	22, 3
	lwz 3, 0(17)
	cmpldi	22, 0
	addi 3, 3, 1
	stw 3, 0(17)
	stw 22, 1608(29)
	beq	0, .LBB3_29
	addi 24, 1, 184
	addi 4, 30, 867
	std 15, 184(1)
	mr	3, 24
	bl append_str
	clrldi	4, 22, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 22
	li 5, 0
	mr	6, 15
	stb 14, 0(3)
	mr	3, 26
	bl hddlog_write
	li 3, 3
	stw 3, 8(17)
	stw 22, 12(17)
	b .LBB3_32
.LBB3_29:
	ld 22, 76(17)
	addi 20, 1, 184
	addi 4, 30, 1053
	mr	3, 20
	std 22, 1744(29)
	std 15, 184(1)
	bl append_str
	mr	3, 20
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	li 4, 0
	mr	5, 22
	mr	6, 15
	stb 14, 0(3)
	mr	3, 26
	bl hddlog_write
	addi 4, 30, 741
	mr	3, 20
	std 15, 184(1)
	bl append_str
	mr	3, 20
	mr	4, 24
	bl format_hex64
	addi 4, 30, 213
	mr	3, 20
	bl append_str
	mr	3, 20
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	mr	4, 24
	mr	5, 22
	mr	6, 15
	stb 14, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 16391
	li 4, 4
	rotldi	9, 3, 61
	li 3, 176
	mr	5, 31
	mr	6, 24
	mr	7, 22
	lis 8, 16
	mr	27, 30
	li 30, 4
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	19, 3
	mr	3, 20
	addi 4, 4, 1
	stw 4, 0(17)
	addi 4, 27, 549
	stw 19, 1612(29)
	ld 18, 76(17)
	std 18, 1752(29)
	std 15, 184(1)
	bl append_str
	clrldi	4, 19, 32
	mr	3, 20
	bl format_dec
	addi 4, 27, 510
	mr	3, 20
	bl append_str
	mr	3, 20
	mr	4, 18
	bl format_hex64
	ld 3, 184(1)
	mr	4, 19
	mr	5, 18
	mr	6, 15
	stb 14, 0(3)
	mr	3, 26
	bl hddlog_write
	cmpldi	19, 0
	beq	0, .LBB3_67
	stw 30, 8(17)
	stw 19, 12(17)
.LBB3_31:
	ld 27, 136(1)
	addi 24, 1, 184
	mr	3, 24
	addi 4, 27, 775
	std 15, 184(1)
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	ld 3, 184(1)
	li 30, 0
	mr	4, 22
	li 5, 0
	mr	6, 15
	stb 30, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 175
	li 4, 4
	li 7, 0
	mr	5, 31
	mr	6, 22
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(17)
	addi 4, 27, 663
	stw 3, 1620(29)
	mr	3, 24
	std 15, 184(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 23
	li 5, 0
	mr	6, 15
	stb 30, 0(3)
	mr	3, 26
	mr	30, 27
	bl hddlog_write
.LBB3_32:
	addi 24, 1, 184
	addi 4, 30, 952
	std 15, 184(1)
	mr	3, 24
	bl append_str
	ld 3, 184(1)
	li 30, 0
	li 4, 4
	mr	5, 31
	mr	6, 15
	stb 30, 0(3)
	mr	3, 25
	bl hddlog_write
	li 3, 171
	li 4, 4
	li 6, 0
	li 7, 0
	mr	5, 31
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	27, 3
	addi 4, 4, 1
	stw 4, 0(17)
	stw 3, 1624(29)
	ld 3, 136(1)
	addi 4, 3, 709
	mr	3, 24
	std 15, 184(1)
	bl append_str
	clrldi	4, 27, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 27
	li 5, 0
	mr	6, 15
	stb 30, 0(3)
	mr	3, 26
	ld 30, 136(1)
	bl hddlog_write
.LBB3_33:
	addi 4, 30, 1026
	addi 3, 1, 184
	std 15, 184(1)
	bl append_str
	lwz 3, 8(17)
	cmplwi	3, 0
	beq	0, .LBB3_35
	addi 27, 1, 184
	addi 4, 30, 523
	mr	3, 27
	bl append_str
	lwz 4, 8(17)
	mr	3, 27
	bl format_dec
	b .LBB3_36
.LBB3_35:
	addi 4, 30, 577
	addi 3, 1, 184
	bl append_str
	li 3, 0
	stw 3, 12(17)
.LBB3_36:
	ld 3, 184(1)
	li 4, 0
	addi 6, 1, 192
	stb 4, 0(3)
	mr	3, 28
	lwz 4, 8(17)
	lwz 5, 0(17)
.LBB3_37:
	bl hddlog_write
	lwz 3, -4(17)
	ori 3, 3, 2
	stw 3, -4(17)
.LBB3_38:
	cmplwi	16, 7
	rldic 3, 16, 6, 26
	add 3, 29, 3
	addi 28, 3, 1024
	stdx 28, 0, 15
	beq	0, .LBB3_56
	cmplwi	16, 1
	beq	0, .LBB3_51
	cmplwi	16, 2
	beq	0, .LBB3_55
	cmplwi	16, 3
	beq	0, .LBB3_53
	cmplwi	16, 4
	beq	0, .LBB3_48
	cmplwi	16, 5
	beq	0, .LBB3_50
	cmplwi	16, 6
	beq	0, .LBB3_49
	cmplwi	16, 0
	bne	0, .LBB3_52
	ld 30, .LC0@toc(2)
	addi 3, 1, 192
	addi 4, 30, 605
	bl append_str
	lbz 3, 2072(29)
	cmpldi	3, 6
	bgt	0, .LBB3_58
	sldi 3, 3, 3
	add 3, 30, 3
	ld 4, 1360(3)
	b .LBB3_59
.LBB3_48:
	ld 30, .LC0@toc(2)
	addi 29, 1, 192
	mr	3, 29
	addi 4, 30, 24
	bl append_str
	lwz 4, 0(17)
	mr	3, 29
	bl format_dec
	addi 4, 30, 130
	mr	3, 29
	bl append_str
	lwz 4, 68(17)
	mr	3, 29
	bl format_dec
	addi 4, 30, 199
	mr	3, 29
	bl append_str
	lhz 4, 72(17)
	mr	3, 29
	bl format_dec
	addi 4, 30, 309
	mr	3, 29
	bl append_str
	lwz 4, 4(17)
	mr	3, 29
	b .LBB3_61
.LBB3_49:
	ld 3, .LC0@toc(2)
	addi 27, 1, 192
	addi 4, 3, 619
	mr	3, 27
	bl append_str
	ld 4, 1760(29)
	b .LBB3_57
.LBB3_50:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 485
	bl append_str
	lwz 4, 1720(29)
	mr	3, 27
	bl format_dec
	addi 4, 30, 206
	mr	3, 27
	bl append_str
	lwz 4, 1724(29)
	mr	3, 27
	bl format_dec
	addi 4, 30, 317
	mr	3, 27
	bl append_str
	lwz 4, 1728(29)
	b .LBB3_64
.LBB3_51:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 369
	bl append_str
	lhz 4, 2144(29)
	mr	3, 27
	bl format_hex16
	addi 4, 30, 418
	mr	3, 27
	bl append_str
	lhz 4, 2208(29)
	mr	3, 27
	bl format_hex16
	addi 4, 30, 285
	mr	3, 27
	bl append_str
	ld 3, 2152(29)
	clrldi	4, 3, 32
	b .LBB3_60
.LBB3_52:
	ld 3, .LC0@toc(2)
	addi 4, 3, 678
	addi 3, 1, 192
	bl append_str
	b .LBB3_65
.LBB3_53:
	ld 30, .LC0@toc(2)
	addi 3, 1, 192
	addi 4, 30, 301
	bl append_str
	lbz 3, 1736(29)
	cmpldi	3, 3
	bgt	0, .LBB3_62
	sldi 3, 3, 3
	add 3, 30, 3
	ld 4, 1144(3)
	b .LBB3_63
.LBB3_55:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 473
	bl append_str
	lwz 4, 2096(29)
	mr	3, 27
	bl format_dec
	addi 4, 30, 293
	mr	3, 27
	bl append_str
	lwz 4, 2100(29)
	mr	3, 27
	bl format_dec
	addi 4, 30, 48
	mr	3, 27
	bl append_str
	lwz 4, 2088(29)
	b .LBB3_64
.LBB3_56:
	ld 30, .LC0@toc(2)
	addi 27, 1, 192
	mr	3, 27
	addi 4, 30, 450
	bl append_str
	ld 4, 1744(29)
	mr	3, 27
	bl format_hex64
	addi 4, 30, 325
	mr	3, 27
	bl append_str
	ld 4, 1752(29)
.LBB3_57:
	mr	3, 27
	bl format_hex64
	b .LBB3_65
.LBB3_58:
	addi 4, 30, 33
.LBB3_59:
	addi 27, 1, 192
	mr	3, 27
	bl append_str
	addi 4, 30, 185
	mr	3, 27
	bl append_str
	lhz 4, 2074(29)
	mr	3, 27
	bl format_hex32
	addi 4, 30, 192
	mr	3, 27
	bl append_str
	lbz 4, 2076(29)
.LBB3_60:
	mr	3, 27
.LBB3_61:
	bl format_hex32
	b .LBB3_65
.LBB3_62:
	addi 4, 30, 118
.LBB3_63:
	addi 27, 1, 192
	mr	3, 27
	bl append_str
	addi 4, 30, 53
	mr	3, 27
	bl append_str
	lwz 4, 1720(29)
	mr	3, 27
	bl format_dec
	addi 4, 30, 293
	mr	3, 27
	bl append_str
	lwz 4, 1692(29)
.LBB3_64:
	mr	3, 27
	bl format_dec
.LBB3_65:
	ldx 3, 0, 15
	li 4, 0
	stb 4, 0(3)
.LBB3_66:
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
.LBB3_67:
	addi 3, 29, 1628
	addi 4, 29, 1792
	std 24, 40(1)
	addi 5, 29, 1680
	addi 6, 29, 1856
	std 6, 88(1)
	ori 18, 23, 4096
	ori 14, 24, 4096
	std 5, 80(1)
	addi 10, 27, 8
	li 5, 0
	li 6, 0
	li 7, 0
	std 4, 72(1)
	li 4, 0
	li 8, 5
	std 3, 64(1)
	mr	3, 31
	li 9, 1
	std 23, 32(1)
	std 14, 56(1)
	std 18, 48(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	mr	30, 27
	beq	0, .LBB3_33
	addi 3, 29, 1632
	addi 4, 29, 1800
	std 14, 56(1)
	addi 5, 29, 1684
	addi 6, 29, 1864
	std 6, 88(1)
	addi 10, 30, 12
	li 6, 1
	std 5, 80(1)
	li 5, 36
	li 7, 1
	li 8, 6
	li 9, 2
	std 4, 72(1)
	li 4, 18
	std 3, 64(1)
	mr	3, 31
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	beq	0, .LBB3_33
	li 3, 37
	addi 4, 29, 1919
	mtctr 3
	li 3, 0
	bdz .LBB3_71
.LBB3_70:
	lbzx 5, 18, 3
	addi 6, 4, 1
	addi 3, 3, 1
	stb 5, 1(4)
	mr	4, 6
	bdnz .LBB3_70
.LBB3_71:
	addi 3, 29, 1636
	addi 4, 29, 1808
	std 14, 56(1)
	addi 5, 29, 1688
	addi 6, 29, 1872
	std 6, 88(1)
	addi 10, 30, 16
	li 6, 1
	std 5, 80(1)
	li 5, 8
	li 7, 1
	li 8, 7
	li 9, 4
	std 4, 72(1)
	li 4, 37
	std 3, 64(1)
	mr	3, 31
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	beq	0, .LBB3_33
	lbz 3, 0(18)
	addi 7, 30, 2
	lbz 4, 1(18)
	lbz 5, 2(18)
	lbz 6, 3(18)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1712(29)
	lbz 3, 4(18)
	lbz 4, 5(18)
	lbz 5, 6(18)
	lbz 6, 7(18)
	rlwimi 6, 5, 8, 16, 23
	addi 5, 29, 2008
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 1716(29)
	addi 6, 29, 2032
	li 3, 2
	li 4, 3
	bl query_vuart_param
	addi 5, 29, 2012
	addi 6, 29, 2040
	addi 7, 30, 20
	li 3, 10
	li 4, 3
	bl query_vuart_param
	addi 5, 29, 2016
	addi 6, 29, 2048
	lwa 20, 2012(29)
	addi 7, 30, 136
	li 3, 10
	li 4, 0
	bl query_vuart_param
	lwz 3, 1628(29)
	cmplwi	3, 0
	bne	0, .LBB3_74
	ld 3, 1792(29)
	cmpldi	3, 0
	beq	0, .LBB3_104
.LBB3_74:
	li 3, 0
.LBB3_75:
	lwz 4, 1636(29)
	cmplwi	4, 0
	bne	0, .LBB3_77
	ld 4, 1808(29)
	cmpldi	4, 0
	beq	0, .LBB3_78
.LBB3_77:
	li 3, 0
.LBB3_78:
	lwz 4, 1716(29)
	xori 4, 4, 2048
	or 4, 20, 4
	cmpwi	4, 0
	bc 4, 2, .LBB3_96
	cmpwi	3, 0
	bc 12, 2, .LBB3_96
	addi 3, 29, 2112
	addi 4, 29, 2120
	std 14, 56(1)
	addi 5, 29, 2128
	addi 6, 29, 2136
	std 6, 88(1)
	addi 10, 30, 333
	li 6, 1
	std 5, 80(1)
	li 5, 32
	li 7, 1
	li 8, 16
	li 9, 256
	std 4, 72(1)
	li 4, 70
	std 3, 64(1)
	mr	3, 31
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	beq	0, .LBB3_33
	lbz 3, 6(18)
	addi 5, 29, 2152
	addi 6, 29, 2168
	addi 10, 30, 758
	li 7, 1
	lbz 4, 7(18)
	li 8, 17
	li 9, 512
	rlwimi 4, 3, 8, 0, 23
	addi 3, 29, 2148
	sth 4, 2144(29)
	addi 4, 29, 2160
	std 6, 88(1)
	li 6, 1
	std 4, 80(1)
	li 4, 173
	std 5, 72(1)
	li 5, 2048
	std 3, 64(1)
	mr	3, 31
	std 14, 56(1)
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	beq	0, .LBB3_33
	addi 3, 29, 2176
	addi 4, 29, 2184
	std 14, 56(1)
	addi 5, 29, 2192
	addi 6, 29, 2200
	std 6, 88(1)
	addi 10, 30, 342
	li 6, 1
	std 5, 80(1)
	li 5, 32
	li 7, 1
	li 8, 18
	li 9, 1024
	std 4, 72(1)
	li 4, 70
	std 3, 64(1)
	mr	3, 31
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_atapi_cmd
	cmplwi	3, 1
	beq	0, .LBB3_33
	lbz 3, 6(18)
	ori 20, 24, 6144
	lbz 4, 7(18)
	rlwimi 4, 3, 8, 0, 23
	addi 3, 18, 2048
	sth 4, 2208(29)
	bl format_auth_request
	addi 21, 1, 184
	addi 4, 30, 1209
	std 15, 184(1)
	mr	3, 21
	bl append_str
	ld 3, 184(1)
	mr	27, 30
	li 30, 0
	li 4, 10
	li 5, 112
	stb 30, 0(3)
	mr	3, 25
	mr	6, 15
	bl hddlog_write
	li 3, 163
	li 4, 10
	li 6, 112
	li 7, 0
	mr	5, 20
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	19, 3
	addi 4, 4, 1
	stw 4, 0(17)
	addi 4, 27, 887
	ld 20, 76(17)
	stw 3, 2084(29)
	mr	3, 21
	stw 20, 2088(29)
	std 15, 184(1)
	bl append_str
	extsw 4, 19
	mr	3, 21
	bl format_s32
	addi 4, 27, 221
	mr	3, 21
	bl append_str
	clrldi	4, 20, 32
	mr	3, 21
	bl format_dec
	ld 3, 184(1)
	mr	4, 19
	mr	5, 20
	mr	6, 15
	stb 30, 0(3)
	mr	3, 26
	bl hddlog_write
	cmpdi	19, 0
	bc 4, 2, .LBB3_105
	cmpdi	20, 0
	bc 12, 2, .LBB3_105
	addi 3, 18, 2304
	li 4, 112
	li 5, 0
	bl prefill_buffer
	ld 3, 136(1)
	addi 4, 3, 1277
	addi 3, 1, 184
	std 15, 184(1)
	bl append_str
	ld 3, 184(1)
	li 4, 10
	li 5, 112
	mr	6, 15
	stb 30, 0(3)
	mr	3, 25
	bl hddlog_write
	bl native_clock
	nop
	lis 4, 2435
	mr	21, 3
	ori 30, 24, 6400
	li 3, 0
	ori 27, 4, 19840
	li 19, 0
.LBB3_86:
	cmplwi	19, 111
	mr	20, 3
	bgt	0, .LBB3_90
	clrldi	3, 19, 32
	li 4, 10
	or 5, 3, 30
	subfic 6, 3, 112
	li 3, 162
	li 7, 0
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	cmpldi	3, 0
	addi 4, 4, 1
	stw 4, 0(17)
	stw 3, 2092(29)
	ld 3, 76(17)
	bne	0, .LBB3_89
	add 19, 19, 3
	bl native_clock
	nop
	sub	3, 3, 21
	cmpld	3, 27
	addi 3, 20, 1
	blt	0, .LBB3_86
.LBB3_89:
	addi 20, 20, 1
.LBB3_90:
	stw 19, 2096(29)
	stw 20, 2100(29)
	bl native_clock
	nop
	cmplwi	19, 4
	sub	3, 3, 21
	std 3, 2104(29)
	blt	0, .LBB3_106
	lbz 3, 2304(18)
	cmplwi	19, 36
	lbz 4, 2305(18)
	lbz 5, 2306(18)
	lbz 6, 2307(18)
	rlwimi 6, 5, 8, 16, 23
	rlwimi 6, 4, 16, 8, 15
	rlwimi 6, 3, 24, 0, 7
	stw 6, 2080(29)
	blt	0, .LBB3_107
	lbz 3, 2338(18)
	cmplwi	19, 57
	lbz 4, 2339(18)
	rlwimi 4, 3, 8, 0, 23
	sth 4, 2074(29)
	blt	0, .LBB3_107
	lbz 3, 2360(18)
	cmplwi	19, 112
	stb 3, 2076(29)
	blt	0, .LBB3_107
	lhz 3, 2074(29)
	cmplwi	3, 0
	beq	0, .LBB3_114
.LBB3_95:
	li 3, 2
	b .LBB3_108
.LBB3_96:
	li 3, 5
	addi 6, 30, 999
	stb 3, 2072(29)
	li 3, 1
	mr	5, 20
	stb 3, 2073(29)
	mr	3, 21
	lwz 4, 1716(29)
	bl hddlog_write
.LBB3_97:
	addi 3, 29, 1640
	addi 4, 29, 1816
	std 29, 64(1)
	addi 5, 29, 1692
	addi 6, 29, 1880
	std 6, 96(1)
	addi 7, 29, 1720
	addi 8, 29, 1736
	std 8, 112(1)
	addi 10, 30, 143
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
	mr	3, 31
	std 14, 56(1)
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_33
	li 3, 33
	addi 4, 29, 1973
	mtctr 3
	li 3, 0
	bdz .LBB3_100
.LBB3_99:
	lbzx 5, 18, 3
	addi 6, 4, 1
	addi 3, 3, 1
	stb 5, 1(4)
	mr	4, 6
	bdnz .LBB3_99
.LBB3_100:
	addi 3, 29, 1644
	addi 4, 29, 1824
	std 29, 64(1)
	addi 5, 29, 1696
	addi 6, 29, 1888
	std 6, 96(1)
	addi 7, 29, 1724
	addi 8, 29, 1737
	std 8, 112(1)
	addi 10, 30, 70
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
	mr	3, 31
	std 14, 56(1)
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_33
	addi 3, 29, 1648
	addi 4, 29, 1832
	std 29, 64(1)
	addi 5, 29, 1700
	addi 6, 29, 1896
	std 6, 96(1)
	addi 7, 29, 1728
	addi 8, 29, 1738
	std 8, 112(1)
	addi 10, 30, 150
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
	mr	3, 31
	std 14, 56(1)
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_33
	addi 3, 29, 1840
	addi 4, 29, 1704
	std 29, 64(1)
	addi 5, 29, 1904
	addi 6, 29, 1732
	std 6, 104(1)
	addi 7, 29, 1739
	addi 11, 29, 1652
	std 7, 112(1)
	addi 10, 30, 157
	li 6, 2048
	li 7, 3
	li 8, 11
	std 5, 96(1)
	li 5, 1
	li 9, 64
	std 4, 88(1)
	li 4, 16
	std 3, 80(1)
	mr	3, 31
	std 14, 56(1)
	std 18, 48(1)
	std 24, 40(1)
	std 23, 32(1)
	std 11, 72(1)
	bl execute_read_test
	cmplwi	3, 1
	beq	0, .LBB3_33
	addi 24, 1, 184
	addi 4, 30, 809
	std 15, 184(1)
	mr	3, 24
	bl append_str
	mr	3, 24
	mr	4, 22
	bl format_hex64
	addi 4, 30, 563
	mr	3, 24
	bl append_str
	ld 3, 184(1)
	mr	27, 30
	li 30, 0
	mr	4, 22
	lis 5, 16
	stb 30, 0(3)
	mr	3, 25
	mr	6, 15
	bl hddlog_write
	li 3, 177
	li 4, 4
	lis 7, 16
	mr	5, 31
	mr	6, 22
	li 8, 0
	li 9, 0
	bl lv1_hcall
	nop
	lwz 4, 0(17)
	mr	23, 3
	addi 4, 4, 1
	stw 4, 0(17)
	addi 4, 27, 693
	stw 3, 1616(29)
	mr	3, 24
	std 15, 184(1)
	bl append_str
	clrldi	4, 23, 32
	mr	3, 24
	bl format_dec
	ld 3, 184(1)
	mr	4, 23
	li 5, 0
	mr	6, 15
	stb 30, 0(3)
	mr	3, 26
	bl hddlog_write
	b .LBB3_31
.LBB3_104:
	li 3, 1
	b .LBB3_75
.LBB3_105:
	li 3, 6
	stb 3, 2072(29)
	b .LBB3_112
.LBB3_106:
	cmplwi	19, 0
	beq	0, .LBB3_113
.LBB3_107:
	li 3, 4
.LBB3_108:
	stb 3, 2072(29)
	addi 3, 18, 2368
	li 4, 48
	li 5, 0
	li 30, 0
	bl prefill_buffer
	ld 3, 128(1)
	addi 21, 1, 184
	ld 27, 136(1)
	std 3, 184(1)
	addi 4, 27, 930
	mr	3, 21
	bl append_str
	clrldi	4, 19, 32
	mr	3, 21
	bl format_dec
	addi 4, 27, 229
	mr	3, 21
	bl append_str
	clrldi	4, 20, 32
	mr	3, 21
	bl format_dec
	addi 4, 27, 351
	mr	3, 21
	bl append_str
	lhz 4, 2074(29)
	mr	3, 21
	bl format_hex32
	addi 4, 27, 237
	mr	3, 21
	bl append_str
	lbz 4, 2076(29)
	mr	3, 21
	bl format_hex32
	addi 4, 27, 64
	mr	3, 21
	bl append_str
	lbz 3, 2072(29)
	cmpldi	3, 6
	bgt	0, .LBB3_110
	ld 4, 136(1)
	sldi 3, 3, 3
	add 3, 4, 3
	ld 4, 1360(3)
	b .LBB3_111
.LBB3_110:
	ld 3, 136(1)
	addi 4, 3, 33
.LBB3_111:
	addi 3, 1, 184
	bl append_str
	ld 3, 184(1)
	addi 6, 1, 192
	stb 30, 0(3)
	mr	3, 26
	lhz 4, 2074(29)
	lbz 5, 2076(29)
	bl hddlog_write
	ld 15, 128(1)
.LBB3_112:
	ld 30, 136(1)
	ld 31, 144(1)
	b .LBB3_97
.LBB3_113:
	li 3, 3
	b .LBB3_108
.LBB3_114:
	lbz 3, 2076(29)
	cmplwi	3, 0
	beq	0, .LBB3_95
	li 3, 1
	b .LBB3_108
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
	.type	execute_atapi_cmd,@function
execute_atapi_cmd:
.Lfunc_begin9:
.Lfunc_gep9:
	addis 2, 12, .TOC.-.Lfunc_gep9@ha
	addi 2, 2, .TOC.-.Lfunc_gep9@l
.Lfunc_lep9:
	.localentry	execute_atapi_cmd, .Lfunc_lep9-.Lfunc_gep9
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
	stdu 1, -272(1)
	ld 29, 328(1)
	mr	26, 3
	mr	28, 8
	mr	30, 10
	mr	27, 9
	ld 3, 304(1)
	mr	8, 29
	mr	25, 5
	std 0, 288(1)
	ld 21, 336(1)
	ld 24, 312(1)
	bl setup_atapi_block
	cmplwi	25, 0
	addi 23, 1, 48
	beq	0, .LBB9_2
	ld 3, 320(1)
	mr	4, 25
	li 5, 0
	bl prefill_buffer
	ld 22, .LC0@toc(2)
	std 23, 40(1)
	addi 23, 1, 40
	mr	3, 23
	addi 4, 22, 28
	bl append_str
	mr	3, 23
	mr	4, 30
	bl append_str
	addi 4, 22, 591
	mr	3, 23
	bl append_str
	mr	3, 23
	mr	4, 24
	bl format_hex64
	addi 4, 22, 536
	mr	23, 29
	b .LBB9_3
.LBB9_2:
	std 23, 40(1)
	ld 23, .LC0@toc(2)
	addi 29, 1, 40
	mr	3, 29
	addi 4, 23, 28
	bl append_str
	mr	3, 29
	mr	4, 30
	bl append_str
	addi 4, 23, 591
	li 23, 0
	mr	29, 24
.LBB9_3:
	lis 3, 147
	addi 22, 1, 40
	ori 20, 3, 3884
	mr	3, 22
	bl append_str
	mr	3, 22
	mr	4, 29
	bl format_hex64
	ld 3, 40(1)
	li 4, 0
	addi 29, 1, 48
	mr	5, 23
	mr	6, 29
	stb 4, 0(3)
	lis 3, 20562
	mr	4, 24
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 248
	mr	4, 26
	li 5, 1
	mr	6, 24
	li 7, 64
	mr	8, 23
	mr	9, 25
	bl lv1_hcall
	nop
	mr	25, 3
	lwz 3, -8(20)
	cmpldi	25, 0
	addi 3, 3, 1
	stw 3, -8(20)
	stw 25, 0(21)
	beq	0, .LBB9_9
	lwz 3, 0(20)
	cmplwi	3, 0
	bne	0, .LBB9_6
	stw 28, 0(20)
.LBB9_6:
	lwz 3, 4(20)
	cmplwi	3, 0
	bne	0, .LBB9_8
	stw 25, 4(20)
.LBB9_8:
	ld 27, .LC0@toc(2)
	addi 28, 1, 40
	std 29, 40(1)
	mr	3, 28
	addi 4, 27, 76
	bl append_str
	mr	3, 28
	mr	4, 30
	bl append_str
	addi 4, 27, 428
	mr	3, 28
	bl append_str
	extsw 4, 25
	mr	3, 28
	bl format_s32
	ld 3, 40(1)
	li 4, 0
	li 5, 0
	mr	6, 29
	stb 4, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	mr	4, 25
	bl hddlog_write
	li 3, -1
	b .LBB9_14
.LBB9_9:
	ld 23, 360(1)
	mr	3, 26
	ld 25, 352(1)
	mr	7, 23
	ld 24, 344(1)
	mr	6, 25
	ld 4, 68(20)
	mr	5, 24
	bl poll_completion
	cmplwi	3, 0
	beq	0, .LBB9_13
	lwz 3, -4(20)
	or 3, 3, 27
	stw 3, -4(20)
	lwz 3, 0(20)
	cmplwi	3, 0
	bne	0, .LBB9_12
	stw 28, 0(20)
.LBB9_12:
	ld 27, .LC0@toc(2)
	addi 28, 1, 40
	std 29, 40(1)
	mr	3, 28
	addi 4, 27, 378
	bl append_str
	mr	3, 28
	mr	4, 30
	bl append_str
	addi 4, 27, 1111
	mr	3, 28
	bl append_str
	ld 3, 40(1)
	li 4, 0
	mr	6, 29
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 0(25)
	ld 5, 0(23)
	bl hddlog_write
	li 3, 1
	b .LBB9_14
.LBB9_13:
	ld 27, .LC0@toc(2)
	addi 28, 1, 40
	std 29, 40(1)
	mr	3, 28
	addi 4, 27, 76
	bl append_str
	mr	3, 28
	mr	4, 30
	bl append_str
	addi 4, 27, 725
	mr	3, 28
	bl append_str
	ld 4, 0(24)
	mr	3, 28
	bl format_hex64
	addi 4, 27, 229
	mr	3, 28
	bl append_str
	lwz 4, 0(25)
	mr	3, 28
	bl format_dec
	ld 3, 40(1)
	li 4, 0
	mr	6, 29
	stb 4, 0(3)
	lis 3, 20559
	ori 3, 3, 21332
	ld 5, 0(24)
	bl hddlog_write
	li 3, 0
.LBB9_14:
	addi 1, 1, 272
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
.Lfunc_end9:
	.size	execute_atapi_cmd, .Lfunc_end9-.Lfunc_begin9

	.p2align	2
	.type	query_vuart_param,@function
query_vuart_param:
.Lfunc_begin10:
.Lfunc_gep10:
	addis 2, 12, .TOC.-.Lfunc_gep10@ha
	addi 2, 2, .TOC.-.Lfunc_gep10@l
.Lfunc_lep10:
	.localentry	query_vuart_param, .Lfunc_lep10-.Lfunc_gep10
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
	addi 4, 23, 439
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
	addi 4, 23, 461
	ld 3, 76(3)
	std 3, 0(29)
	mr	3, 28
	std 30, 40(1)
	bl append_str
	mr	3, 28
	mr	4, 27
	bl append_str
	addi 4, 23, 82
	mr	3, 28
	bl append_str
	extsw 4, 25
	mr	3, 28
	bl format_s32
	addi 4, 23, 245
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
.Lfunc_end10:
	.size	query_vuart_param, .Lfunc_end10-.Lfunc_begin10

	.p2align	2
	.type	format_auth_request,@function
format_auth_request:
.Lfunc_begin11:
.Lfunc_gep11:
	addis 2, 12, .TOC.-.Lfunc_gep11@ha
	addi 2, 2, .TOC.-.Lfunc_gep11@l
.Lfunc_lep11:
	.localentry	format_auth_request, .Lfunc_lep11-.Lfunc_gep11
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
.Lfunc_end11:
	.size	format_auth_request, .Lfunc_end11-.Lfunc_begin11

	.p2align	2
	.type	format_s32,@function
format_s32:
.Lfunc_begin12:
.Lfunc_gep12:
	addis 2, 12, .TOC.-.Lfunc_gep12@ha
	addi 2, 2, .TOC.-.Lfunc_gep12@l
.Lfunc_lep12:
	.localentry	format_s32, .Lfunc_lep12-.Lfunc_gep12
	cmpwi	4, 0
	bge 0, .LBB12_2
	ld 5, 0(3)
	neg 4, 4
	addi 6, 5, 1
	std 6, 0(3)
	li 6, 45
	stb 6, 0(5)
.LBB12_2:
	clrldi	4, 4, 32
	b format_dec
	#TC_RETURNd8 format_dec 0
	.long	0
	.quad	0
.Lfunc_end12:
	.size	format_s32, .Lfunc_end12-.Lfunc_begin12

	.p2align	2
	.type	prefill_buffer,@function
prefill_buffer:
.Lfunc_begin13:
	addi 4, 4, 1
	addi 3, 3, -1
	mtctr 4
.LBB13_1:
	bdzlr
	addi 4, 3, 1
	stb 5, 1(3)
	mr	3, 4
	b .LBB13_1
	.long	0
	.quad	0
.Lfunc_end13:
	.size	prefill_buffer, .Lfunc_end13-.Lfunc_begin13

	.p2align	2
	.type	format_hex32,@function
format_hex32:
.Lfunc_begin14:
.Lfunc_gep14:
	addis 2, 12, .TOC.-.Lfunc_gep14@ha
	addi 2, 2, .TOC.-.Lfunc_gep14@l
.Lfunc_lep14:
	.localentry	format_hex32, .Lfunc_lep14-.Lfunc_gep14
	li 5, 8
	b format_hex_n
	#TC_RETURNd8 format_hex_n 0
	.long	0
	.quad	0
.Lfunc_end14:
	.size	format_hex32, .Lfunc_end14-.Lfunc_begin14

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
	stdu 1, -464(1)
	std 0, 480(1)
	std 28, 432(1)
	ld 28, 512(1)
	std 19, 360(1)
	mr	19, 3
	lis 3, 147
	std 16, 336(1)
	mr	16, 4
	li 4, 2048
	std 18, 352(1)
	mr	18, 5
	li 5, 165
	std 31, 456(1)
	ori 31, 3, 3884
	mr	3, 28
	std 14, 320(1)
	std 15, 328(1)
	std 17, 344(1)
	mr	17, 7
	std 20, 368(1)
	std 21, 376(1)
	std 22, 384(1)
	mr	22, 6
	std 23, 392(1)
	mr	23, 10
	std 24, 400(1)
	std 25, 408(1)
	std 26, 416(1)
	std 27, 424(1)
	std 29, 440(1)
	std 30, 448(1)
	std 9, 40(1)
	std 8, 48(1)
	ld 25, 552(1)
	ld 21, 544(1)
	ld 29, 520(1)
	ld 27, 504(1)
	ld 26, 496(1)
	ld 24, 536(1)
	bl prefill_buffer
	li 4, 64
	mr	3, 26
	li 5, 0
	li 30, 0
	bl prefill_buffer
	ld 14, .LC0@toc(2)
	li 3, 40
	li 4, 12
	stb 3, 0(26)
	li 3, 1
	addi 15, 1, 56
	stb 30, 2(26)
	addi 20, 1, 64
	stb 30, 3(26)
	stb 30, 4(26)
	stb 16, 5(26)
	stb 3, 8(26)
	stw 4, 32(26)
	addi 4, 14, 28
	stw 18, 36(26)
	stw 22, 40(26)
	stw 17, 44(26)
	stw 3, 48(26)
	mr	3, 15
	std 29, 56(26)
	std 20, 56(1)
	bl append_str
	mr	3, 15
	mr	4, 23
	bl append_str
	addi 4, 14, 164
	mr	3, 15
	bl append_str
	mr	3, 15
	mr	4, 16
	mr	16, 27
	bl format_dec
	addi 4, 14, 269
	mr	3, 15
	bl append_str
	mr	3, 15
	mr	4, 17
	mr	17, 19
	bl format_dec
	addi 4, 14, 171
	mr	3, 15
	bl append_str
	mr	3, 15
	mr	4, 18
	bl format_dec
	addi 4, 14, 94
	mr	3, 15
	bl append_str
	mr	3, 15
	mr	4, 22
	bl format_dec
	ld 3, 56(1)
	mr	4, 27
	mr	5, 29
	mr	6, 20
	stb 30, 0(3)
	lis 3, 20562
	ori 3, 3, 17696
	bl hddlog_write
	li 3, 248
	li 5, 1
	mr	4, 19
	mr	6, 27
	li 7, 64
	mr	8, 29
	li 9, 2048
	bl lv1_hcall
	nop
	mr	22, 3
	lwz 3, -8(31)
	cmpldi	22, 0
	addi 3, 3, 1
	stw 3, -8(31)
	stw 22, 0(24)
	beq	0, .LBB15_5
	lwz 3, 0(31)
	cmplwi	3, 0
	bne	0, .LBB15_3
	ld 3, 48(1)
	stw 3, 0(31)
.LBB15_3:
	lwz 3, 4(31)
	mr	24, 21
	cmplwi	3, 0
	bne	0, .LBB15_7
	stw 22, 4(31)
	b .LBB15_7
.LBB15_5:
	ld 18, 560(1)
	mr	3, 17
	mr	5, 21
	mr	6, 25
	ld 27, 40(1)
	mr	7, 18
	ld 4, 68(31)
	bl poll_completion
	cmplwi	3, 0
	mr	24, 21
	beq	0, .LBB15_7
	lwz 3, -4(31)
	addi 30, 1, 56
	addi 4, 14, 378
	or 3, 3, 27
	stw 3, -4(31)
	ld 3, 48(1)
	stw 3, 0(31)
	mr	3, 30
	std 20, 56(1)
	bl append_str
	mr	3, 30
	mr	4, 23
	bl append_str
	addi 4, 14, 1111
	mr	3, 30
	bl append_str
	ld 3, 56(1)
	li 4, 0
	mr	6, 20
	stb 4, 0(3)
	lis 3, 21581
	ori 3, 3, 20256
	lwz 4, 0(25)
	ld 5, 0(18)
	bl hddlog_write
	li 3, 1
	b .LBB15_27
.LBB15_7:
	li 3, 2049
	ld 4, 568(1)
	cmpdi 2, 22, 0
	addi 5, 28, -1
	ld 21, 528(1)
	li 19, 0
	mtctr 3
	ld 3, 576(1)
	bdz .LBB15_9
.LBB15_8:
	lbz 6, 1(5)
	addi 5, 5, 1
	xori 6, 6, 165
	cntlzw	6, 6
	srwi 6, 6, 5
	add 19, 19, 6
	bdnz .LBB15_8
.LBB15_9:
	cmplwi	19, 2048
	li 30, 0
	stw 19, 0(4)
	beq	0, .LBB15_19
	lbz 4, 1(28)
	cmplwi	4, 67
	bne	0, .LBB15_15
	lbz 4, 2(28)
	cmplwi	4, 68
	bne	0, .LBB15_15
	lbz 4, 3(28)
	cmplwi	4, 48
	bne	0, .LBB15_15
	lbz 4, 4(28)
	cmplwi	4, 48
	bne	0, .LBB15_15
	lbz 4, 5(28)
	li 30, 2
	cmplwi	4, 49
	beq	0, .LBB15_19
.LBB15_15:
	li 4, 2049
	addi 5, 28, -1
	mtctr 4
	li 4, 0
	bdz .LBB15_17
.LBB15_16:
	lbz 6, 1(5)
	addi 5, 5, 1
	cntlzw	6, 6
	srwi 6, 6, 5
	add 4, 4, 6
	bdnz .LBB15_16
.LBB15_17:
	cmplwi	4, 2048
	li 30, 1
	beq	0, .LBB15_19
	li 30, 3
.LBB15_19:
	stb 30, 0(3)
	addi 4, 14, 76
	std 20, 56(1)
	addi 20, 1, 56
	mr	3, 20
	bl append_str
	mr	3, 20
	mr	4, 23
	bl append_str
	addi 4, 14, 82
	mr	3, 20
	bl append_str
	clrldi	4, 22, 32
	mr	3, 20
	bl format_dec
	addi 4, 14, 398
	mr	3, 20
	bl append_str
	ld 4, 0(24)
	mr	3, 20
	bl format_hex64
	addi 4, 14, 100
	mr	3, 20
	bl append_str
	rldic 3, 30, 3, 29
	add 3, 14, 3
	ld 4, 1144(3)
	mr	3, 20
	bl append_str
	addi 4, 14, 38
	mr	3, 20
	bl append_str
	clrldi	4, 19, 32
	mr	3, 20
	bl format_dec
	addi 4, 14, 229
	mr	3, 20
	bl append_str
	lwz 4, 0(25)
	mr	3, 20
	bl format_dec
	addi 4, 14, 43
	mr	3, 20
	bl append_str
	mr	3, 20
	mr	4, 28
	bl format_bytes_hex
	addi 4, 14, 106
	mr	3, 20
	bl append_str
	addi 4, 28, 16
	mr	3, 20
	bl format_bytes_hex
	addi 4, 14, 178
	mr	3, 20
	bl append_str
	ld 4, 56(1)
	li 3, 9
	addi 5, 28, 39
	mtctr 3
	addi 3, 4, -1
.LBB15_20:
	addi 4, 3, 1
	bdz .LBB15_24
	lbz 6, 1(5)
	addi 5, 5, 1
	addi 7, 6, -32
	clrlwi	7, 7, 24
	cmplwi	7, 95
	blt	0, .LBB15_23
	li 6, 46
.LBB15_23:
	stb 6, 1(3)
	mr	3, 4
	b .LBB15_20
.LBB15_24:
	std 4, 56(1)
	ld 4, .LC0@toc(2)
	addi 3, 1, 56
	bl append_str
	ld 3, 56(1)
	li 4, 0
	addi 6, 1, 64
	stb 4, 0(3)
	lis 3, 20559
	mr	4, 22
	ori 3, 3, 21332
	ld 5, 0(24)
	bl hddlog_write
	bc 4, 10, .LBB15_26
	ld 3, 0(24)
	clrldi	3, 3, 56
	cmpldi	3, 2
	li 3, 0
	bne	0, .LBB15_27
.LBB15_26:
	mr	3, 17
	mr	4, 26
	mr	5, 16
	mr	6, 28
	mr	7, 29
	mr	8, 21
	bl do_request_sense
	li 3, -1
.LBB15_27:
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
.Lfunc_end15:
	.size	execute_read_test, .Lfunc_end15-.Lfunc_begin15

	.p2align	2
	.type	format_hex_n,@function
format_hex_n:
.Lfunc_begin16:
.Lfunc_gep16:
	addis 2, 12, .TOC.-.Lfunc_gep16@ha
	addi 2, 2, .TOC.-.Lfunc_gep16@l
.Lfunc_lep16:
	.localentry	format_hex_n, .Lfunc_lep16-.Lfunc_gep16
	ld 6, .LC0@toc(2)
	addi 7, 5, 1
	rlwinm 5, 5, 2, 0, 29
	mtctr 7
.LBB16_1:
	addi 5, 5, -4
	bdzlr
	srd 7, 4, 5
	ld 8, 0(3)
	clrldi	7, 7, 60
	add 7, 6, 7
	lbz 7, 792(7)
	addi 9, 8, 1
	std 9, 0(3)
	stb 7, 0(8)
	b .LBB16_1
	.long	0
	.quad	0
.Lfunc_end16:
	.size	format_hex_n, .Lfunc_end16-.Lfunc_begin16

	.p2align	2
	.type	setup_atapi_block,@function
setup_atapi_block:
.Lfunc_begin17:
.Lfunc_gep17:
	addis 2, 12, .TOC.-.Lfunc_gep17@ha
	addi 2, 2, .TOC.-.Lfunc_gep17@l
.Lfunc_lep17:
	.localentry	setup_atapi_block, .Lfunc_lep17-.Lfunc_gep17
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
	cmplwi	25, 3
	li 3, 4
	stb 25, 0(27)
	beq	0, .LBB17_7
	cmplwi	25, 18
	beq	0, .LBB17_7
	cmplwi	25, 70
	beq	0, .LBB17_5
	cmplwi	25, 173
	bne	0, .LBB17_8
	li 5, 0
	li 3, 9
	stb 5, 1(27)
	li 4, 8
	li 6, 7
	stb 5, 6(27)
	li 5, 0
	b .LBB17_6
.LBB17_5:
	li 3, 8
	li 4, 7
	li 5, 2
	li 6, 1
.LBB17_6:
	stbx 5, 27, 6
	srwi 5, 26, 8
	stbx 5, 27, 4
.LBB17_7:
	stbx 26, 27, 3
.LBB17_8:
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
.Lfunc_end17:
	.size	setup_atapi_block, .Lfunc_end17-.Lfunc_begin17

	.p2align	2
	.type	poll_completion,@function
poll_completion:
.Lfunc_begin18:
.Lfunc_gep18:
	addis 2, 12, .TOC.-.Lfunc_gep18@ha
	addi 2, 2, .TOC.-.Lfunc_gep18@l
.Lfunc_lep18:
	.localentry	poll_completion, .Lfunc_lep18-.Lfunc_gep18
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
.LBB18_1:
	addi 21, 21, -1
	li 24, 1
	cmpldi	21, 0
	bc 4, 1, .LBB18_6
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
	beq	0, .LBB18_5
	bl native_clock
	nop
	sub	3, 3, 29
	cmpld	3, 20
	bgt	0, .LBB18_6
	addi 22, 22, 1
	b .LBB18_1
.LBB18_5:
	ld 3, 76(23)
	li 24, 0
	std 3, 0(27)
	addi 3, 22, 1
	stw 3, 0(28)
.LBB18_6:
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
.Lfunc_end18:
	.size	poll_completion, .Lfunc_end18-.Lfunc_begin18

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
	addi 4, 6, 792
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
	std 29, -24(1)
	std 30, -16(1)
	stdu 1, -128(1)
	std 0, 144(1)
	mr	30, 8
	mr	29, 6
	addi 6, 8, 1656
	addi 8, 8, 1848
	std 4, 32(1)
	ld 4, .LC0@toc(2)
	addi 9, 30, 1708
	addi 10, 30, 1912
	std 7, 56(1)
	li 7, 1
	std 5, 40(1)
	li 5, 18
	std 10, 88(1)
	addi 10, 4, 124
	li 4, 3
	std 9, 80(1)
	li 9, 128
	std 8, 72(1)
	li 8, 12
	std 6, 64(1)
	li 6, 1
	std 29, 48(1)
	bl execute_atapi_cmd
	li 3, 19
	addi 4, 29, -1
	mtctr 3
	addi 5, 30, 1955
	li 3, 0
	bdz .LBB20_2
.LBB20_1:
	lbz 6, 1(4)
	addi 7, 5, 1
	addi 4, 4, 1
	addi 3, 3, 1
	stb 6, 1(5)
	mr	5, 7
	bdnz .LBB20_1
.LBB20_2:
	addi 1, 1, 128
	ld 0, 16(1)
	mtlr 0
	ld 30, -16(1)
	ld 29, -24(1)
	blr
	.long	0
	.quad	0
.Lfunc_end20:
	.size	do_request_sense, .Lfunc_end20-.Lfunc_begin20

	.p2align	2
	.type	format_hex16,@function
format_hex16:
.Lfunc_begin21:
.Lfunc_gep21:
	addis 2, 12, .TOC.-.Lfunc_gep21@ha
	addi 2, 2, .TOC.-.Lfunc_gep21@l
.Lfunc_lep21:
	.localentry	format_hex16, .Lfunc_lep21-.Lfunc_gep21
	li 5, 4
	b format_hex_n
	#TC_RETURNd8 format_hex_n 0
	.long	0
	.quad	0
.Lfunc_end21:
	.size	format_hex16, .Lfunc_end21-.Lfunc_begin21

	.type	.L_MergedGlobals,@object
	.section	.data.rel.ro,"aw",@progbits
	.p2align	3, 0x0
.L_MergedGlobals:
	.asciz	"'"
	.asciz	"p2"
	.asciz	"OK"
	.asciz	"tur"
	.asciz	"inq"
	.asciz	"cap"
	.asciz	"p10"
	.asciz	"HC="
	.asciz	"pre "
	.asciz	"NONE"
	.asciz	" a5="
	.asciz	" w0="
	.asciz	" WR="
	.asciz	" A5="
	.asciz	" hdd="
	.asciz	" vrd="
	.asciz	"pio_0"
	.asciz	"post "
	.asciz	": rc="
	.asciz	"SHORT"
	.asciz	" bsz="
	.asciz	" cls="
	.asciz	" w16="
	.asciz	"ZEROS"
	.asciz	"OTHER"
	.asciz	"sense"
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
	.asciz	" SKIP="
	.asciz	" 0_A5="
	.asciz	" rgn=0x"
	.asciz	" bytes="
	.asciz	" polls="
	.asciz	" flg=0x"
	.asciz	" val=0x"
	.asciz	"TIMEOUT"
	.asciz	"SKIPPED"
	.asciz	" proto="
	.asciz	"DATA_OK"
	.asciz	" RDS=0x"
	.asciz	" POLLS="
	.asciz	"PIO16: "
	.asciz	" TMO=0x"
	.asciz	" 17_A5="
	.asciz	" BUS=0x"
	.asciz	"get_cfg1"
	.asciz	"get_cfg2"
	.asciz	" stat=0x"
	.asciz	"ERR_STAT"
	.asciz	"PROF1=0x"
	.asciz	"timeout: "
	.asciz	"ERR_WRITE"
	.asciz	" async=0x"
	.asciz	"UNCHANGED"
	.asciz	" PROF2=0x"
	.asciz	": send_rc="
	.asciz	"pre vuart_"
	.asciz	"DMA RGN=0x"
	.asciz	"post vuart_"
	.asciz	"AUTH: READ="
	.asciz	"PIO: 16_A5="
	.asciz	" bus=4 dev=2"
	.asciz	" bus_addr=0x"
	.asciz	"step failed="
	.asciz	" buf_lpar=0x"
	.asciz	"post map: rc="
	.asciz	" len=0x100000"
	.asciz	"clean success"
	.asciz	": cmd_lpar=0x"
	.asciz	"P11-W2 AUTH: "
	.asciz	"CDVD LPAR: 0x"
	.asciz	"scan: rom_cnt="
	.asciz	"post open: rc="
	.asciz	"post free: rc="
	.asciz	"P11-W2 RUNNING"
	.asciz	"post unmap: rc="
	.asciz	"post close: rc="
	.asciz	": rc=0 async=0x"
	.asciz	"pre map: lpar=0x"
	.asciz	"read_disc_struct"
	.asciz	"pre free: rgn=0x"
	.asciz	"0123456789abcdef"
	.asciz	"pre unmap: rgn=0x"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"/tmp/netemu_log.bin"
	.asciz	"post dma_alloc: rc="
	.asciz	"post auth_write: rc="
	.asciz	"pre open: bus=4 dev=2"
	.asciz	"post auth_read: read="
	.asciz	"pre close: bus=4 dev=2"
	.asciz	"boot: ps2_netemu_p11_W2"
	.asciz	"auth skipped: guard failed"
	.asciz	"finish: ps2_netemu_p11_W2 "
	.asciz	"post dma_alloc: rc=0 rgn=0x"
	.asciz	"grd ok: lpar & ea sanity pass"
	.asciz	" timed out; halting hypercalls"
	.space	2
	.quad	.L_MergedGlobals+408
	.quad	.L_MergedGlobals+112
	.quad	.L_MergedGlobals+277
	.quad	.L_MergedGlobals+118
	.asciz	"grd reject: sanity failed (0 hc)"
	.asciz	"pre auth_write: port=10 len=0x70"
	.asciz	"pre dma_alloc: sz=0x100000 pexp=20"
	.asciz	"pre auth_read: port=10 max_len=0x70"
	.asciz	"finish: ps2_netemu_p11_W2 rejected by guard"
	.space	3
	.quad	.L_MergedGlobals+33
	.quad	.L_MergedGlobals+5
	.quad	.L_MergedGlobals+360
	.quad	.L_MergedGlobals+253
	.quad	.L_MergedGlobals+88
	.quad	.L_MergedGlobals+261
	.quad	.L_MergedGlobals+388
	.size	.L_MergedGlobals, 1416

.L.str.78 = .L_MergedGlobals
	.size	.L.str.78, 2
.L.str.19 = .L_MergedGlobals+2
	.size	.L.str.19, 3
.L.str.62 = .L_MergedGlobals+5
	.size	.L.str.62, 3
.L.str.16 = .L_MergedGlobals+8
	.size	.L.str.16, 4
.L.str.17 = .L_MergedGlobals+12
	.size	.L.str.17, 4
.L.str.18 = .L_MergedGlobals+16
	.size	.L.str.18, 4
.L.str.20 = .L_MergedGlobals+20
	.size	.L.str.20, 4
.L.str.95 = .L_MergedGlobals+24
	.size	.L.str.95, 4
.L.str.49 = .L_MergedGlobals+28
	.size	.L.str.49, 5
.L.str.61 = .L_MergedGlobals+33
	.size	.L.str.61, 5
.L.str.74 = .L_MergedGlobals+38
	.size	.L.str.74, 5
.L.str.75 = .L_MergedGlobals+43
	.size	.L.str.75, 5
.L.str.92 = .L_MergedGlobals+48
	.size	.L.str.92, 5
.L.str.94 = .L_MergedGlobals+53
	.size	.L.str.94, 5
.L.str.2 = .L_MergedGlobals+58
	.size	.L.str.2, 6
.L.str.34 = .L_MergedGlobals+64
	.size	.L.str.34, 6
.L.str.36 = .L_MergedGlobals+70
	.size	.L.str.36, 6
.L.str.52 = .L_MergedGlobals+76
	.size	.L.str.52, 6
.L.str.59 = .L_MergedGlobals+82
	.size	.L.str.59, 6
.L.str.65 = .L_MergedGlobals+88
	.size	.L.str.65, 6
.L.str.71 = .L_MergedGlobals+94
	.size	.L.str.71, 6
.L.str.73 = .L_MergedGlobals+100
	.size	.L.str.73, 6
.L.str.76 = .L_MergedGlobals+106
	.size	.L.str.76, 6
.L.str.80 = .L_MergedGlobals+112
	.size	.L.str.80, 6
.L.str.82 = .L_MergedGlobals+118
	.size	.L.str.82, 6
.L.str.83 = .L_MergedGlobals+124
	.size	.L.str.83, 6
.L.str.96 = .L_MergedGlobals+130
	.size	.L.str.96, 6
.L.str.21 = .L_MergedGlobals+136
	.size	.L.str.21, 7
.L.str.35 = .L_MergedGlobals+143
	.size	.L.str.35, 7
.L.str.37 = .L_MergedGlobals+150
	.size	.L.str.37, 7
.L.str.38 = .L_MergedGlobals+157
	.size	.L.str.38, 7
.L.str.68 = .L_MergedGlobals+164
	.size	.L.str.68, 7
.L.str.70 = .L_MergedGlobals+171
	.size	.L.str.70, 7
.L.str.77 = .L_MergedGlobals+178
	.size	.L.str.77, 7
.L.str.85 = .L_MergedGlobals+185
	.size	.L.str.85, 7
.L.str.86 = .L_MergedGlobals+192
	.size	.L.str.86, 7
.L.str.97 = .L_MergedGlobals+199
	.size	.L.str.97, 7
.L.str.100 = .L_MergedGlobals+206
	.size	.L.str.100, 7
.L.str.13 = .L_MergedGlobals+213
	.size	.L.str.13, 8
.L.str.28 = .L_MergedGlobals+221
	.size	.L.str.28, 8
.L.str.31 = .L_MergedGlobals+229
	.size	.L.str.31, 8
.L.str.33 = .L_MergedGlobals+237
	.size	.L.str.33, 8
.L.str.60 = .L_MergedGlobals+245
	.size	.L.str.60, 8
.L.str.64 = .L_MergedGlobals+253
	.size	.L.str.64, 8
.L.str.66 = .L_MergedGlobals+261
	.size	.L.str.66, 8
.L.str.69 = .L_MergedGlobals+269
	.size	.L.str.69, 8
.L.str.81 = .L_MergedGlobals+277
	.size	.L.str.81, 8
.L.str.89 = .L_MergedGlobals+285
	.size	.L.str.89, 8
.L.str.91 = .L_MergedGlobals+293
	.size	.L.str.91, 8
.L.str.93 = .L_MergedGlobals+301
	.size	.L.str.93, 8
.L.str.98 = .L_MergedGlobals+309
	.size	.L.str.98, 8
.L.str.101 = .L_MergedGlobals+317
	.size	.L.str.101, 8
.L.str.104 = .L_MergedGlobals+325
	.size	.L.str.104, 8
.L.str.23 = .L_MergedGlobals+333
	.size	.L.str.23, 9
.L.str.25 = .L_MergedGlobals+342
	.size	.L.str.25, 9
.L.str.32 = .L_MergedGlobals+351
	.size	.L.str.32, 9
.L.str.63 = .L_MergedGlobals+360
	.size	.L.str.63, 9
.L.str.87 = .L_MergedGlobals+369
	.size	.L.str.87, 9
.L.str.54 = .L_MergedGlobals+378
	.size	.L.str.54, 10
.L.str.67 = .L_MergedGlobals+388
	.size	.L.str.67, 10
.L.str.72 = .L_MergedGlobals+398
	.size	.L.str.72, 10
.L.str.79 = .L_MergedGlobals+408
	.size	.L.str.79, 10
.L.str.88 = .L_MergedGlobals+418
	.size	.L.str.88, 10
.L.str.53 = .L_MergedGlobals+428
	.size	.L.str.53, 11
.L.str.57 = .L_MergedGlobals+439
	.size	.L.str.57, 11
.L.str.103 = .L_MergedGlobals+450
	.size	.L.str.103, 11
.L.str.58 = .L_MergedGlobals+461
	.size	.L.str.58, 12
.L.str.90 = .L_MergedGlobals+473
	.size	.L.str.90, 12
.L.str.99 = .L_MergedGlobals+485
	.size	.L.str.99, 12
.L.str.3 = .L_MergedGlobals+497
	.size	.L.str.3, 13
.L.str.15 = .L_MergedGlobals+510
	.size	.L.str.15, 13
.L.str.48 = .L_MergedGlobals+523
	.size	.L.str.48, 13
.L.str.51 = .L_MergedGlobals+536
	.size	.L.str.51, 13
.L.str.14 = .L_MergedGlobals+549
	.size	.L.str.14, 14
.L.str.40 = .L_MergedGlobals+563
	.size	.L.str.40, 14
.L.str.47 = .L_MergedGlobals+577
	.size	.L.str.47, 14
.L.str.50 = .L_MergedGlobals+591
	.size	.L.str.50, 14
.L.str.84 = .L_MergedGlobals+605
	.size	.L.str.84, 14
.L.str.102 = .L_MergedGlobals+619
	.size	.L.str.102, 14
.L.str.1 = .L_MergedGlobals+633
	.size	.L.str.1, 15
.L.str.8 = .L_MergedGlobals+648
	.size	.L.str.8, 15
.L.str.43 = .L_MergedGlobals+663
	.size	.L.str.43, 15
.L.str.105 = .L_MergedGlobals+678
	.size	.L.str.105, 15
.L.str.41 = .L_MergedGlobals+693
	.size	.L.str.41, 16
.L.str.45 = .L_MergedGlobals+709
	.size	.L.str.45, 16
.L.str.56 = .L_MergedGlobals+725
	.size	.L.str.56, 16
.L.str.12 = .L_MergedGlobals+741
	.size	.L.str.12, 17
.L.str.24 = .L_MergedGlobals+758
	.size	.L.str.24, 17
.L.str.42 = .L_MergedGlobals+775
	.size	.L.str.42, 17
HEX_DIGITS = .L_MergedGlobals+792
	.size	HEX_DIGITS, 17
.L.str.39 = .L_MergedGlobals+809
	.size	.L.str.39, 18
hddlog_init.path = .L_MergedGlobals+827
	.size	hddlog_init.path, 20
hddlog_write.path = .L_MergedGlobals+847
	.size	hddlog_write.path, 20
.L.str.10 = .L_MergedGlobals+867
	.size	.L.str.10, 20
.L.str.27 = .L_MergedGlobals+887
	.size	.L.str.27, 21
.L.str.7 = .L_MergedGlobals+908
	.size	.L.str.7, 22
.L.str.30 = .L_MergedGlobals+930
	.size	.L.str.30, 22
.L.str.44 = .L_MergedGlobals+952
	.size	.L.str.44, 23
.L.str = .L_MergedGlobals+975
	.size	.L.str, 24
.L.str.22 = .L_MergedGlobals+999
	.size	.L.str.22, 27
.L.str.46 = .L_MergedGlobals+1026
	.size	.L.str.46, 27
.L.str.11 = .L_MergedGlobals+1053
	.size	.L.str.11, 28
.L.str.6 = .L_MergedGlobals+1081
	.size	.L.str.6, 30
.L.str.55 = .L_MergedGlobals+1111
	.size	.L.str.55, 31
class_to_str.STRS = .L_MergedGlobals+1144
	.size	class_to_str.STRS, 32
.L.str.4 = .L_MergedGlobals+1176
	.size	.L.str.4, 33
.L.str.26 = .L_MergedGlobals+1209
	.size	.L.str.26, 33
.L.str.9 = .L_MergedGlobals+1242
	.size	.L.str.9, 35
.L.str.29 = .L_MergedGlobals+1277
	.size	.L.str.29, 36
.L.str.5 = .L_MergedGlobals+1313
	.size	.L.str.5, 44
auth_verdict_to_str.STRS = .L_MergedGlobals+1360
	.size	auth_verdict_to_str.STRS, 56
	.ident	"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"
	.section	".note.GNU-stack","",@progbits
	.section	.toc,"aw",@progbits
.LC0:
	.tc .L_MergedGlobals[TC],.L_MergedGlobals
