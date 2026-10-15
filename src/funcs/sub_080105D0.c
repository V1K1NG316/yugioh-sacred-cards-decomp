#include "global.h"

extern u8 gUnk_02023298[];
extern u8 *gUnk_08D34AB4;

u32 sub_0802691C(u8 *, u32);
u32 sub_080271C4(u32);

void sub_080105D0(void)
{
    if (sub_0802691C(gUnk_02023298, 0x182) == 0) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = sub_080271C4(2);
    }
}
