#include "global.h"

extern u8 gUnk_02023490[];

void sub_08030940(u8 id)
{
    u8 *base = gUnk_02023490;
    u8 *p = base + (id << 5);

    if (p[0x14] - 1 < 0) {
        p[0x14] = 0x1A;
    }
    p[0x14] = p[0x14] - 1;
}
