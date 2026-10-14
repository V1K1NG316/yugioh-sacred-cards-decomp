#include "global.h"

extern u16 *gUnk_020232AC[];

u32 sub_08023114(u16);

u32 sub_080230E4(void)
{
    u8 acc = 0;
    u8 i;

    for (i = 0; i < 5; i++)
        acc |= sub_08023114(gUnk_020232AC[i][0]);
    return acc;
}
