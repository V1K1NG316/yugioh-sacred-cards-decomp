#include "global.h"

extern u8 gUnk_02023120[];
extern u8 gUnk_02023140[];

void sub_0802356C(void)
{
    u8 *d = gUnk_02023140;
    u8 *s = gUnk_02023120;

    *(u16 *)(d + 0) = *(u16 *)(s + 0);
    d[0xA] = s[8];
    *(u16 *)(d + 6) = *(u16 *)(s + 2);
    *(u16 *)(d + 8) = *(u16 *)(s + 4);
    *(u16 *)(d + 0xC) = *(u16 *)(s + 0xC);
    d[0x16] = s[0x14];
    *(u16 *)(d + 0x12) = *(u16 *)(s + 0xE);
    *(u16 *)(d + 0x14) = *(u16 *)(s + 0x10);
}
