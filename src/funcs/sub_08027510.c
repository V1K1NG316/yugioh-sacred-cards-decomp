#include "global.h"

void sub_08021E50(u16);

extern u8 gUnk_02023438[];

void sub_08027510(void)
{
    u8 v;
    u32 w;

    sub_08021E50(0x36);
    v = gUnk_02023438[1];
    w = v + 1;
    gUnk_02023438[1] = w;
    if ((u8)w > 4)
        gUnk_02023438[1] = v;
}
