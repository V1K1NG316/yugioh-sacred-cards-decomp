#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023298[];

u32 sub_0802691C(u8 *, s32);
u32 sub_080271C4(s32);

void sub_0800F444(void)
{
    if (sub_0802691C(gUnk_02023298, 0x177) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = sub_080271C4(2);
}
