#include "global.h"

extern u8 gUnk_02020C50[];

void sub_08014480(void)
{
    u16 *d = (u16 *)0x02020AF8;
    u8 *p = gUnk_02020C50;

    d[0] = *(s8 *)(p + 4);
    d[1] = p[8] - 1;
}
