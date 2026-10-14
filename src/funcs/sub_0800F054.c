#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_080271C4(s32);

void sub_0800F054(void)
{
    u32 *p = (u32 *)(gUnk_08D34AB4 + 0x14F0);
    u32 v;

    if (*p == 0x7EE0ACE9)
        return;
    v = sub_080271C4(2);
    if (*p < v)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D582;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
}
