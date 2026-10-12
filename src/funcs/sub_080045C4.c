#include "global.h"

extern u8 gUnk_02020770[];

void sub_080045C4(u16 i)
{
    u8 *p = &gUnk_02020770[i];

    if (*p < 0xFA)
        *p = *p + 1;
    else
        *p = 0xFA;
}
