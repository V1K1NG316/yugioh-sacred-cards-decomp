#include "global.h"

extern u32 gUnk_03007FF0[];

void sub_08038034(void)
{
    u32 *p = (u32 *)gUnk_03007FF0[0];
    u32 ident = p[0];

    if (ident != 0x68736D53) {
        *(u16 *)0x040000C6 = 0xB600;
        *(u16 *)0x040000D2 = 0xB600;
        (void)*(volatile u8 *)((u8 *)p + 4);
        *(u8 *)((u8 *)p + 4) = 0;
        p[0] = ident - 10;
    }
}
