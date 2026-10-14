#include "global.h"

extern u8 gUnk_02023438[];

u32 sub_080274D4(u32 a)
{
    gUnk_02023438[4] = 0;
    gUnk_02023438[0] = 0;
    gUnk_02023438[1] = 4;
    gUnk_02023438[2] = 0;
    gUnk_02023438[3] = 4;
    return a;
}
