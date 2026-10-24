#include "global.h"

extern u8 gUnk_02020C50[];
extern u16 gUnk_080EBAF0[];

void sub_08014424(void)
{
    u32 i = 0;
    u8 *p = gUnk_02020C50;
    u16 *d = (u16 *)(p + 0xA);

    for (; i <= 0x27; i++)
        d[i] = gUnk_080EBAF0[i];
}
