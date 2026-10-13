#include "global.h"

extern u16 gUnk_0201FCB0[];

void sub_08003BAC(void)
{
    *(u16 *)0x04000202 = 1;
    gUnk_0201FCB0[0] |= 1;
}
