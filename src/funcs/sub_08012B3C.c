#include "global.h"

extern u8 gUnk_080AC29C[];
extern u16 gUnk_02023468;

u32 sub_08039CAC(u32, u32);

void sub_08012B3C(u32 a)
{
    u8 b = gUnk_080AC29C[sub_08039CAC(a, 3)];
    u16 x = 0x10 - b;

    gUnk_02023468 = (x & 0x1F) | ((b & 0x1F) << 8);
}
