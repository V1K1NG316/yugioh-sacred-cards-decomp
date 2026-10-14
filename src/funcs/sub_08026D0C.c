#include "global.h"

s32 sub_08026D0C(u32 *p, u16 id)
{
    s8 i;

    for (i = 0; i <= 4; i++) {
        if (*(u16 *)*p++ == id)
            return i;
    }
    return 0;
}
