#include "global.h"

extern u8 gUnk_02023284[];
extern u8 *gUnk_08D34AB4;

u32 sub_080268FC(u32);

void sub_0800B32C(void)
{
    if (sub_080268FC((u32)gUnk_02023284) == 5)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF99744;
}
