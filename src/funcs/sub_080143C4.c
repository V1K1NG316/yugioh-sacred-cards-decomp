/* compiler: agbcc (A37) */
#include "global.h"

void sub_080144E8(void);

extern u8 gUnk_02020C50[];

void sub_080143C4(u16 v)
{
    *(u16 *)(gUnk_02020C50 + 0xA + gUnk_02020C50[8] * 2) = v;
    gUnk_02020C50[8] = gUnk_02020C50[8] + 1;
    sub_080144E8();
}
