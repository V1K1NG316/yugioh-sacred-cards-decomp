#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86BB[];

void sub_0801C344(void)
{
    volatile u8 *p = gUnk_020214D0;
    gUnk_020214D0[0x7EA] = gUnk_080C86BB[p[0x7EA]];
}
