#include "global.h"

extern u8 gUnk_02023298[];
extern u8 *gUnk_08D34AB4;

u32 sub_080268FC(u8 *);

void sub_0800FCFC(void)
{
    u32 *p;
    u32 v;

    if (sub_080268FC(gUnk_02023298) == 0) {
        p = (u32 *)(gUnk_08D34AB4 + 0x14F0);
        v = 0x7EE0ACE9;
    } else {
        p = (u32 *)(gUnk_08D34AB4 + 0x14F0);
        v = 0x7FF32E8E;
    }
    *p = v;
}
