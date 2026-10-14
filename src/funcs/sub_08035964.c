#include "global.h"

extern u8 gUnk_089C56B0[];

u8 sub_08018150(u16);
void sub_0803692C(const void *, void *, u32);

void sub_08035964(u8 *dst, u16 a)
{
    u8 v = sub_08018150(a);

    if (v != 0)
        sub_0803692C((const void *)(gUnk_089C56B0 + (v << 6)), dst, 0x20);
}
