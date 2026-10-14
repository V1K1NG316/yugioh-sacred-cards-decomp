#include "global.h"

extern u8 gUnk_02023298[];
extern u8 *gUnk_08D34AB4;

s32 sub_080268FC(u8 *);

void sub_0800FF7C(void)
{
    u8 *p = gUnk_02023298;

    if (sub_080268FC(p) <= 3) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else if (sub_080268FC(p - 0x14) == 5) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF5517B;
    }
}
