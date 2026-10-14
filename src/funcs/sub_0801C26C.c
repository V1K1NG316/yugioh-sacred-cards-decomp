#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86A5[];

void sub_0801C26C(void)
{
    volatile u8 *p = gUnk_020214D0;

    gUnk_020214D0[0x7E8] = gUnk_080C86A5[p[0x7E8]];
}
