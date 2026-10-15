#include "global.h"

extern u8 gUnk_02023298[];
u32 sub_080268FC(u8 *);

extern u8 *gUnk_08D34AB4;

void sub_08010E80(void)
{
    if (sub_080268FC(gUnk_02023298) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF32E8D;
    }
}
