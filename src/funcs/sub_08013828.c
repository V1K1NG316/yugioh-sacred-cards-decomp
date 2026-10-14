#include "global.h"

extern u8 gUnk_080AC390[];
extern u8 *gUnk_08D35BD0;

u32 sub_08013828(void)
{
    if (gUnk_080AC390[gUnk_08D35BD0[7] * 8] == 0)
        return 0;
    return 1;
}
