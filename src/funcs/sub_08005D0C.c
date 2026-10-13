#include "global.h"

extern u8 gUnk_0201FCC0[];

void sub_08021E50(u16);
void sub_0800465C(u8);

void sub_08005D0C(void)
{
    sub_08021E50(0x37);
    if (gUnk_0201FCC0[4] <= 8) {
        gUnk_0201FCC0[2] = gUnk_0201FCC0[4];
        sub_0800465C(gUnk_0201FCC0[2]);
    }
}
