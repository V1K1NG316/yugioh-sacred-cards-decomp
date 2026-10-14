#include "global.h"

extern u8 gUnk_02023490[];

void sub_08030960(u8 id)
{
    u8 *base = gUnk_02023490;
    u8 *p = base + (id << 5);

    p[0x14] = 0x13;
}
