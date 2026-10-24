#include "global.h"

void sub_0803B4A0(u8 *dst, u32 n)
{
    u32 tmp;
    u8 *p = dst;

    while ((tmp = n--) != 0)
        *p++ = 0;
}
