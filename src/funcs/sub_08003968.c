#include "global.h"

void sub_08003968(void)
{
    volatile u32 zero = 0;
    volatile u32 *dma = (volatile u32 *)0x040000D4;

    dma[0] = (u32)&zero;
    dma[1] = 0x02000000;
    dma[2] = 0x85010000;
    (void)dma[2];
    zero = 0;
    dma[0] = (u32)&zero;
    dma[1] = 0x03000000;
    dma[2] = 0x85001F80;
    (void)dma[2];
}
