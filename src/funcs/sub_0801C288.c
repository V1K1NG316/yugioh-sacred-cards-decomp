#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86AA[];

void sub_0801C288(void)
{
    volatile u8 *p = gUnk_020214D0;

    gUnk_020214D0[0x7E8] = gUnk_080C86AA[p[0x7E8]];
}
