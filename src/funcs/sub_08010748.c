#include "global.h"

extern u8 gUnk_02023298[];
extern u8 *gUnk_08D34AB4;

u32 sub_0802691C(u8 *, u32);

void sub_08010748(void)
{
    if (sub_0802691C(gUnk_02023298, 0x2E2) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else if (sub_0802691C(gUnk_02023298, 0x352) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF32E92;
    }
}
