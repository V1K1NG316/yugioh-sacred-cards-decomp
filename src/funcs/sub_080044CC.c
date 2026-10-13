#include "global.h"

extern u16 gUnk_0201FCC0[];

void sub_08021E50(u16);

void sub_080044CC(void)
{
    u16 n;
    u16 v = gUnk_0201FCC0[0];

    gUnk_0201FCC0[0] = (n = v + 1);
    if ((n << 16) > 0x3830000)
        gUnk_0201FCC0[0] = v - 0x383;
    sub_08021E50(0x36);
}
