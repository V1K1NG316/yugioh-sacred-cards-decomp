#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08027040(u32, u32);

void sub_0800F3FC(void)
{
    if ((u8)sub_08027040(1, 5) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF7745D;
}
