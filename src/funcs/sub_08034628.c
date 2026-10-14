#include "global.h"

u32 sub_0803460C(void);
u32 sub_08039370(u32, u32);

u16 sub_08034628(u16 a, u16 b)
{
    u16 v = (u16)sub_0803460C();

    return a + sub_08039370(v, b - a + 1);
}
