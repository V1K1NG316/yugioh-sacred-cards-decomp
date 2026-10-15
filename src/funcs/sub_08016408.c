#include "global.h"

extern u16 gUnk_080B4B40[];
extern u16 gUnk_02020D30[];

u32 sub_08016408(void)
{
    u16 i;

    for (i = 0; gUnk_080B4B40[i] != 0; i++) {
        if (gUnk_02020D30[8] == gUnk_080B4B40[i])
            return 1;
    }
    return 0;
}
