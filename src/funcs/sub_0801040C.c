#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08026EEC(u32);

void sub_0801040C(void)
{
    if ((u8)sub_08026EEC(4) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7F083244;
    }
}
