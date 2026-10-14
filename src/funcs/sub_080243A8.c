#include "global.h"

void sub_080243A8(u8 *p)
{
    u8 v = p[2];

    if (*(s8 *)(p + 2) <= 0x7E)
        p[2] = v + 1;
}
