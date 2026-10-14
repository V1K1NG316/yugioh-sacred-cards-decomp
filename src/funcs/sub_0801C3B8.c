#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86D2[];

void sub_0801C3B8(void)
{
    volatile u8 *p = gUnk_020214D0;

    gUnk_020214D0[0x7EA] = gUnk_080C86D2[p[0x7EA]];
}
