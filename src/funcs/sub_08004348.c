#include "global.h"

extern u8 gUnk_02020770[];

void sub_08004348(u16 a, u8 b)
{
    u8 *p = &gUnk_02020770[a];

    if (b > *p)
        *p = 0;
    else
        *p = *p - b;
}
