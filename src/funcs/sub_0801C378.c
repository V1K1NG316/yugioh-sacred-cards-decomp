#include "global.h"

extern u8 gUnk_020214D0[];
extern u8 gUnk_080C86BE[];

void sub_0801C378(void)
{
    volatile u8 *p = gUnk_020214D0;
    gUnk_020214D0[0x7EA] = gUnk_080C86BE[p[0x7EA]];
}
