#include "global.h"

extern u16 gUnk_02020C5A[];

u32 sub_080145E8(void)
{
    u8 i;

    for (i = 0; i < 0x28; i++)
        if (gUnk_02020C5A[i] == 0)
            return 0;
    return 1;
}
