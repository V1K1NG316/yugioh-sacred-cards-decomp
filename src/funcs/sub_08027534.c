#include "global.h"

void sub_08021E50(u16);

extern u8 gUnk_02023438[];

void sub_08027534(void)
{
    u32 v;

    sub_08021E50(0x36);
    v = gUnk_02023438[0] + 1;
    gUnk_02023438[0] = v;
    if ((u8)v == 5)
        gUnk_02023438[0] = 0;
}
