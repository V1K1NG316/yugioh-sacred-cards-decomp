#include "global.h"

extern u8 gUnk_0200D400[];

void sub_0803692C(u32, u32, u32);

void sub_0801EA58(void)
{
    u8 *p = gUnk_0200D400;

    sub_0803692C((u32)p, 0x0600D000, 0xC00);
    p += 0xFFFFD800;
    sub_0803692C((u32)p, 0x0600A800, 0x400);
}
