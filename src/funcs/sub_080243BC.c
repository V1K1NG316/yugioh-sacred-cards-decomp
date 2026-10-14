#include "global.h"

void sub_080243BC(u8 *p)
{
    u8 v = p[2];

    if (*(s8 *)(p + 2) > -0x80)
        p[2] = v - 1;
}
