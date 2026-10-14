#include "global.h"

void sub_08021E50(u16);

extern u8 gUnk_02023438[];

void sub_08027558(void)
{
    sub_08021E50(0x36);
    if (gUnk_02023438[0] == 0)
        gUnk_02023438[0] = 5;
    gUnk_02023438[0] = gUnk_02023438[0] - 1;
}
