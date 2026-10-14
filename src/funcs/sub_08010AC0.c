#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026FD8(u32, u32);

void sub_08010AC0(void)
{
    if ((u8)sub_08026FD8(1, 1) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D572;
    }
}
