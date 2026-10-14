#include "global.h"

extern u8 gUnk_0200D400[];

void sub_0803692C(u32, u32, u32);

void sub_0801EAC0(void)
{
    u8 *p = gUnk_0200D400;

    sub_0803692C((u32)p, 0x0600D000, 0x800);
    p += 0xFFFFD000;
    sub_0803692C((u32)p, 0x0600A000, 0x400);
}
