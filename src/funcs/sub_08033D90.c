/* compiler: agbcc (A37) */
#include "global.h"

extern u8 gUnk_02023700[];
extern u8 gUnk_08D4F434[];

void sub_08033D90(u32 x)
{
    gUnk_02023700[x >> 3] &= ~gUnk_08D4F434[x & 7];
}
