#include "global.h"

void sub_0803692C(void *, void *, u32);

/* Re-arms the two sound FIFO DMA channels and reloads the engine's DMA block.  The engine
   work-area word must hold the ident 0x68736D53, or one of the two "unlocked" values, for
   anything to happen. */
void sub_08037FB8(void)
{
    u8 *info = *(u8 **)0x03007FF0;
    u32 v;

    if ((u32)(*(u32 *)info + 0x978C92AD) > 1)
        return;

    *(u32 *)info += 10;

    if ((*(volatile u32 *)0x040000C4 & 0x02000000) != 0)
        *(volatile u32 *)0x040000C4 = 0x84400004;
    if ((*(volatile u32 *)0x040000D0 & 0x02000000) != 0)
        *(volatile u32 *)0x040000D0 = 0x84400004;

    *(volatile u16 *)0x040000C6 = 0x0400;
    *(volatile u16 *)0x040000D2 = 0x0400;

    v = 0;
    sub_0803692C(&v, info + 0x350, 0x05000318);
}
