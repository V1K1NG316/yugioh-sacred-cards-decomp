#include "global.h"

void sub_08003B98(void);

void sub_08003B18(void)
{
    volatile u32 *dma;

    sub_08003B98();
    *(u32 *)0x0201CB24 = 0x08003B95;
    dma = (volatile u32 *)0x040000D4;
    dma[0] = 0x080000FC;
    dma[1] = 0x03000400;
    dma[2] = 0x84000200;
    (void)dma[2];
    *(u32 *)0x03007FFC = 0x03000400;
}
