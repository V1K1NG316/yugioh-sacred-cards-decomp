#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_080270A8(u32, u32);

void sub_0800BFF8(void)
{
    if ((u8)sub_080270A8(1, 0x5DC) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF99742;
}
