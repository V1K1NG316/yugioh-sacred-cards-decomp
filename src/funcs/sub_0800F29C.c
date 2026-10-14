#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023160[];

u32 sub_080271C4(s32);

void sub_0800F29C(void)
{
    if (gUnk_02023160[0xF0] == 2)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = sub_080271C4(2);
}
