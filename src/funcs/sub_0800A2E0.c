#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_080271C4(u32);

void sub_0800A2E0(void)
{
    if (*(u32 *)(gUnk_08D34AB4 + 0x14F0) != 0x7EE0ACE9)
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) += sub_080271C4(2);
}
