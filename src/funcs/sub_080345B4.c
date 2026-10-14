#include "global.h"

u32 sub_0803458C(void);
u32 sub_08039370(u32, u32);

u8 sub_080345B4(u8 a, u8 b)
{
    u8 v;

    if (a == b)
        return a;
    v = sub_0803458C();
    return a + sub_08039370(v, b - a + 1);
}
