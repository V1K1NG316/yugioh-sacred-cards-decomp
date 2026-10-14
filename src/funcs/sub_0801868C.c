#include "global.h"

extern u8 *gUnk_08D36418;

u32 sub_0801868C(void)
{
    u32 r = 0;

    if (gUnk_08D36418[4] > 0xF)
        r = 1;
    return r;
}
