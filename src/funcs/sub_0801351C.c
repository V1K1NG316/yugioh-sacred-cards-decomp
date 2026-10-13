#include "global.h"

extern u16 *gUnk_08D359E4;

void sub_0801351C(void)
{
    u16 *p = gUnk_08D359E4;

    if (*p - p[2] > 0x48)
        *p = *p - 0x48;
    else
        *p = p[2];
}
