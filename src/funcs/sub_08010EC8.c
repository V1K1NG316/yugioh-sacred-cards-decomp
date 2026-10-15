#include "global.h"

extern u8 gUnk_02023298[];
u32 sub_080269DC(u8 *, u32);

extern u8 *gUnk_08D34AB4;

void sub_08010EC8(void)
{
    if (sub_080269DC(gUnk_02023298, 1) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EF2D57C;
    }
}
