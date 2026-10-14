#include "global.h"

u32 sub_08026CE4(u32 *p, u16 id)
{
    s8 i;

    for (i = 0; i <= 4; i++) {
        if (*(u16 *)*p++ == id)
            return 1;
    }
    return 0;
}
