/* compiler: agbcc (A37) */
#include "global.h"

extern u8 gUnk_02021CC0[];

u32 sub_0801B758(u16 i, u8 v)
{
    if (v > gUnk_02021CC0[i])
        return 0;
    return 1;
}
