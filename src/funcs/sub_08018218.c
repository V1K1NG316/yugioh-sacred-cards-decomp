#include "global.h"

extern u8 gUnk_02020D88[];

u32 sub_08018218(void)
{
    u32 found = 0;
    u8 i;

    for (i = 0; i < 2; i++)
        if (gUnk_02020D88[i] == 2)
            found = 1;
    return found;
}
