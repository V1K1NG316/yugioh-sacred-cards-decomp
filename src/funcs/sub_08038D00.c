#include "global.h"

extern u32 gUnk_089DF7D4[];

void sub_08038E2C(u32, u8 *, u32);

void sub_08038D00(u32 a, u8 *p)
{
    u8 *q = *(u8 **)(p + 0x40);
    u8 b = *q;

    *(u8 **)(p + 0x40) = q + 1;
    sub_08038E2C(a, p, gUnk_089DF7D4[b]);
}
