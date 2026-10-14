#include "global.h"

extern u8 gUnk_02023284[];
u32 sub_0802690C(u8 *);

extern u8 *gUnk_08D34AB4;

void sub_08010A10(void)
{
    if (sub_0802690C(gUnk_02023284) == 5) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF99743;
    }
}
