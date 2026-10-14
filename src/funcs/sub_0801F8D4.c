#include "global.h"

extern u16 gUnk_02023038[];

void sub_0801F8D4(void)
{
    u32 i = 0;
    u16 z = 0;
    u16 *p = gUnk_02023038;

    do {
        *p++ = z;
        i++;
    } while (i < 4);
}
