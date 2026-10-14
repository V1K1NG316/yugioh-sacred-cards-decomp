#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023298[];

s32 sub_0802691C(u8 *, s32);

void sub_0800F098(void)
{
    u8 *p = gUnk_02023298;

    if (sub_0802691C(p, 4) > 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D571;
    else if (sub_0802691C(p, 0x23) > 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D571;
    else if (sub_0802691C(p, 0x361) > 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D571;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
}
