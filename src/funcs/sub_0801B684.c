#include "global.h"

void sub_0801B644(u8);

extern u8 gUnk_020214D0[];

void sub_0801B684(void)
{
    u32 v = gUnk_020214D0[0x7E9] + 1;

    gUnk_020214D0[0x7E9] = v;
    if ((u8)v > 8)
        gUnk_020214D0[0x7E9] = 0;
    sub_0801B644(gUnk_020214D0[0x7E9]);
}
