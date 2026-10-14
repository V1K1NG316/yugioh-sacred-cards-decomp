#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023298[];

s32 sub_0802691C(u8 *, s32);
u32 sub_080271C4(s32);

void sub_0800F4D4(void)
{
    u8 *p = gUnk_02023298;
    u8 a = sub_0802691C(p, 0x60);
    u8 b = sub_0802691C(p, 0x61);
    u8 c = sub_0802691C(p, 0x62);

    if (a == 0 && b == 0 && c == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = sub_080271C4(2);
}
