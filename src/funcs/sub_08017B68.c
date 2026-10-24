/* compiler: agbcc (A37) */
#include "global.h"

void sub_08017B68(u32 *p)
{
    u8 i;

    for (i = 0; i <= 6; i++) {
        u32 v = *p;

        *p++ = v | (v << 4);
    }
}
