#include "global.h"

extern u8 gUnk_0894B8B4[];

void sub_08035840(u8 *dst)
{
    u32 i;
    u32 j;

    for (i = 0; i <= 3; i++)
    {
        for (j = 0; j <= 0xFF; j++)
            *dst++ = gUnk_0894B8B4[(i << 8) + j];
        dst += 0x300;
    }
}
