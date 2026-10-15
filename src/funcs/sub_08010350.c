#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026F7C(u32, u32);
u32 sub_08026FD8(u32, u32);

void sub_08010350(void)
{
    u8 a = sub_08026F7C(2, 10);
    u32 b = sub_08026FD8(1, 10);

    if ((u8)(a + b) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D573;
    }
}
