#include "global.h"

extern u8 *gUnk_08D34AB4;
extern u8 gUnk_020232C0[];

u32 sub_080268FC(u8 *);

void sub_0800F6E4(void)
{
    if (sub_080268FC(gUnk_020232C0) == 0)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    else
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FB31847;
}
