#include "global.h"

u32 sub_08023C34(u16);

s32 sub_08026A94(u32 *p)
{
    s8 i;

    for (i = 4; i >= 0; i--) {
        if (sub_08023C34(*(u16 *)*p--) == 1)
            return i;
    }
    return 4;
}
