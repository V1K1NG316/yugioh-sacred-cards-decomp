#include "global.h"

extern u8 gUnk_0201FCC0[];

void sub_0800465C(u8);
void sub_08021E50(u16);

void sub_08004630(void)
{
    gUnk_0201FCC0[2] = gUnk_0201FCC0[2] + 1;
    if (gUnk_0201FCC0[2] > 8)
        gUnk_0201FCC0[2] = 0;
    sub_0800465C(gUnk_0201FCC0[2]);
    sub_08021E50(0x36);
}
