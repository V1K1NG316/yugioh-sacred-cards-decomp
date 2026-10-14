#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_02023298[];

u32 sub_080268FC(u8 *);

void sub_0800CB80(void)
{
    u8 *p = gUnk_02023298;

    if (sub_080268FC(p) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else if (sub_080268FC(p - 0x14) == 5)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF9974B;
}
