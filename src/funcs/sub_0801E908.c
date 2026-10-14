#include "global.h"

extern u8 gUnk_0200AC00[];

void sub_0803692C(u32, u32, u32);

void sub_0801E908(void)
{
    u8 *p = gUnk_0200AC00;

    sub_0803692C((u32)p, 0x0600A800, 0x400);
    p += 0x4D20;
    sub_0803692C((u32)p, 0x0600F520, 0xE00);
}
