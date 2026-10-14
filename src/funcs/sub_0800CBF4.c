#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u32 gUnk_02023260[];
extern u8 gUnk_02023298[];

u32 sub_080268FC(u8 *);

void sub_0800CBF4(void)
{
    if (*(u16 *)gUnk_02023260[1] == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else if (sub_080268FC(gUnk_02023298) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FB31849;
}
