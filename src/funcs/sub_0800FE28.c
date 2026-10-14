#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_080271C4(u32);

void sub_0800FE28(void)
{
    u32 *p = (u32 *)(gUnk_08D34AB4 + 0x14F0);
    u32 r;

    if (*p != 0x7EE0ACE9) {
        r = sub_080271C4(2);
        if (*p < r) {
            *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FB3184B;
        } else {
            *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
        }
    }
}
