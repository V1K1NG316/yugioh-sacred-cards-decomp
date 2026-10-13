#include "global.h"

extern u8 gUnk_0201FCC0[];

void sub_08021E50(u16);

void sub_080046C8(void)
{
    gUnk_0201FCC0[3] = gUnk_0201FCC0[3] + 1;
    if (gUnk_0201FCC0[3] > 3)
        gUnk_0201FCC0[3] = 0;
    sub_08021E50(0x36);
}
