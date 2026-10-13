#include "global.h"

extern u16 gUnk_0201FCC0[];

void sub_08021E50(u16);

void sub_080044FC(void)
{
    u16 v = gUnk_0201FCC0[0];

    gUnk_0201FCC0[0] = v - 0x32;
    if ((gUnk_0201FCC0[0] << 16) < 0)
        gUnk_0201FCC0[0] = v + 0x352;
    sub_08021E50(0x36);
}
