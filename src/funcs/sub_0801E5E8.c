#include "global.h"

extern u16 gUnk_02023468[];

void sub_0801E5E8(void)
{
    *(u16 *)0x0202345C = 0xDC;
    gUnk_02023468[0] = 0;
    *(u16 *)0x02023464 = 8;
}
