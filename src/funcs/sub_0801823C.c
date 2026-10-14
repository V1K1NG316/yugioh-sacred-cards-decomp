#include "global.h"

extern u16 gUnk_080BA280[];

u32 sub_0801823C(u16 a)
{
    u16 i;

    for (i = 0; gUnk_080BA280[i] != 0; i++) {
        if (gUnk_080BA280[i] == a)
            return 0;
    }
    return 1;
}
