@ Shell build (milestone Y1): link the original ROM bytes back into a byte-identical GBA image.
@ Every byte comes from the untouched original; nothing is assembled from source yet.

	.section .text
	.global rom_image
rom_image:
	.incbin "private/baserom.gba"
