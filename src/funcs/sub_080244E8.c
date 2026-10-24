/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023260[];

void sub_080244E8(u8 i)
{
    u8 *p = (u8 *)gUnk_02023260[i];

    p[2] |= 3;
}
