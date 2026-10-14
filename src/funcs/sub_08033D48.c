#include "global.h"

extern u8 gUnk_02023700[];

void sub_08033D48(void)
{
    u8 i;

    for (i = 0; i <= 0x31; i++)
        gUnk_02023700[i] = 0;
}
