#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026F34(u32);

void sub_0800B6E4(void)
{
    if ((u8)sub_08026F34(1) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FB3184A;
}
