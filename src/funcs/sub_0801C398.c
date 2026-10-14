#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86C8[];

void sub_0801C398(void)
{
    volatile u8 *p = gUnk_020214D0;

    gUnk_020214D0[0x7EA] = gUnk_080C86C8[p[0x7EA]];
}
