@ Function macros for the generated disassembly (private/asm/rom.s).
@ The names are the ones gbadisasm emits; they match pret's asm/macros/function.inc
@ so gbadisasm output assembles unmodified. No .align here: the disassembler emits
@ its own padding, and the assembler must not add any of its own.

	.macro arm_func_start name
	.global \name
	.type \name, function
	.arm
\name:
	.endm

	.macro arm_func_end name
	.size \name, .-\name
	.endm

	.macro thumb_func_start name
	.global \name
	.type \name, function
	.thumb
	.thumb_func
\name:
	.endm

	.macro non_word_aligned_thumb_func_start name
	.global \name
	.type \name, function
	.thumb
	.thumb_func
\name:
	.endm

	.macro thumb_func_end name
	.size \name, .-\name
	.endm
