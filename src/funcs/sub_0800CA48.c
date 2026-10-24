#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023298[];

u32 sub_0802691C(u8 *, u32);
u32 sub_080268FC(u8 *);

void sub_0800CA48(void)
{
    u8 *p = gUnk_02023298;

    if (sub_0802691C(p, 0x3A) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else if (sub_080268FC(p) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF32E8B;
}
