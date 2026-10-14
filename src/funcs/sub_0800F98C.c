#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026F7C(u32, u32);

void sub_0800F98C(void)
{
    if ((u8)sub_08026F7C(2, 0x14) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D57D;
}
