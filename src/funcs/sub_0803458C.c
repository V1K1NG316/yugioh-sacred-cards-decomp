#include "global.h"

u32 sub_080345E4(void);

u32 sub_0803458C(void)
{
    u8 i;
    u8 r = 0;

    for (i = 0; i <= 7; i++)
    {
        r = r << 1;
        r |= sub_080345E4();
    }
    return r;
}
