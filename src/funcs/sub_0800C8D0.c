#include "global.h"

extern u8 gUnk_020232C0[];
extern u8 *gUnk_08D34AB4;

s32 sub_080268FC(u32);

void sub_0800C8D0(void)
{
    if (sub_080268FC((u32)gUnk_020232C0) <= 1)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EEB5B58;
}
