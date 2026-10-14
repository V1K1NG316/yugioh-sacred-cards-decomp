#include "global.h"

extern u16 gUnk_02023030[];

void sub_0801F8BC(void)
{
    u32 i = 0;
    u16 z = 0;
    u16 *p = gUnk_02023030;

    do {
        *p++ = z;
        i++;
    } while (i < 1);
}
