#include "global.h"

extern u8 gUnk_020214D0[];
extern u16 gUnk_02023474[];

void sub_0801E138(void)
{
    *(u16 *)0x02023450 = gUnk_020214D0[0x7E8] << 5;
    gUnk_02023474[0] = 0;
}
