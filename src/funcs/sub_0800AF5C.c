#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_080271C4(u32);

void sub_0800AF5C(void)
{
    u32 v = sub_080271C4(2);
    u32 *p = (u32 *)(gUnk_08D34AB4 + 0x14F0);

    if (v <= *p)
        *p = 0x7EE0ACE9;
    else
        *p = v + 0x7FC8750B;
}
