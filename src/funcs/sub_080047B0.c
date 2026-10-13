#include "global.h"

extern u16 gUnk_0201FCC0[];
extern u16 gUnk_02020AF8[];

void sub_080047B0(void)
{
    gUnk_02020AF8[0] = gUnk_0201FCC0[0];
    gUnk_02020AF8[1] = 0x383;
}
