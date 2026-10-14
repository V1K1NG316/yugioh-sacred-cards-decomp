#include "global.h"

extern u8 *gUnk_08D36418;

u32 sub_0801862C(void)
{
    u32 r = 0;
    u8 v = gUnk_08D36418[5];
    u8 t;

    if (v != 0)
    {
        r = 1;
        t = v - 4;
        if (t <= 1)
            r = 2;
    }
    return r;
}
