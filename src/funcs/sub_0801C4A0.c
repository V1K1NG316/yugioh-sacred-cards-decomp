/* compiler: agbcc (A37) */
#include "global.h"

extern u8 gUnk_02021140[];

u32 sub_0801C4A0(u16 i, u8 v)
{
    if (v > gUnk_02021140[i])
        return 0;
    return 1;
}
