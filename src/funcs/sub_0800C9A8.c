#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026FD8(u32, u32);

void sub_0800C9A8(void)
{
    *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    if ((u8)sub_08026FD8(1, 2) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF99742;
}
