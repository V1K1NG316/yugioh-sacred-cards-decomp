#include "global.h"

extern u8 gUnk_02023298[];
extern u8 *gUnk_08D34AB4;

s32 sub_080268FC(u8 *, s32);

void sub_08010840(void)
{
    if (sub_080268FC(gUnk_02023298, 0) <= 1) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF32E8C;
    }
}
