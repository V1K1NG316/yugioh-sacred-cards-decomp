#include "global.h"

extern s32 gUnk_020237CC;

u32 sub_080345E4(void)
{
    s32 v = gUnk_020237CC;

    if (v < 0)
    {
        gUnk_020237CC = ((v ^ 0x10000) << 1) | 1;
        return 1;
    }
    gUnk_020237CC = v << 1;
    return 0;
}
