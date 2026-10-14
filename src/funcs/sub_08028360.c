#include "global.h"

extern u32 gUnk_02023260[];

u32 sub_08028360(u8 a)
{
    u16 *p = (u16 *)gUnk_02023260[a];
    u16 v = *p;

    *p = 0;
    return v;
}
