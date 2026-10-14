#include "global.h"

extern u8 gUnk_020237D0[];

u32 sub_08023C34(u16);

u32 sub_08036100(void)
{
    u8 *p = gUnk_020237D0;

    if (sub_08023C34(*(u16 *)p) == 1)
    {
        p[5] = 0xC;
        return 1;
    }
    return 0;
}
