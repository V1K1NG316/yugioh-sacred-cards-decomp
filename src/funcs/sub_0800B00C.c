#include "global.h"

extern u32 *gUnk_08D34AB4;
extern u16 gUnk_0202347C[];

u32 sub_0803691C(void);

void sub_0800B00C(void)
{
    u32 i = sub_0803691C();

    *(u32 *)((u8 *)gUnk_08D34AB4 + 0x14F0) = gUnk_0202347C[i];
}
