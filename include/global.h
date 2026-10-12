/* Minimal types header for the matching-C sources (milestone Y5).
 *
 * The ROM is a 32-bit ARM7TDMI GBA build, so the pret-style names map as below. Only what a
 * matched function needs goes in here; grow it when a function needs more.
 */
#ifndef GUARD_GLOBAL_H
#define GUARD_GLOBAL_H

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;

typedef u8 bool8;
typedef u16 bool16;
typedef u32 bool32;

#define TRUE 1
#define FALSE 0
#define NULL ((void *)0)

#endif /* GUARD_GLOBAL_H */
