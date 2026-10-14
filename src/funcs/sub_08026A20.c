#include "global.h"

s8 sub_08026A20(u32 *p)
{
    u8 i;

    for (i = 0; i < 5; i++) {
        u32 q = *p++;

        if (*(u16 *)q == 0)
            return i;
    }
    return 0;
}
