#include "global.h"

void sub_08017F44(u16 *p)
{
    p[0] = 0;
    p[1] = 0;
    p[2] = 0;
    p[3] = 0;
    *(u8 *)(p + 4) = 0xFF;
}
