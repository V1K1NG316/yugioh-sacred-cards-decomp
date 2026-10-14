#include "global.h"

extern u16 *gUnk_020232C0[];

u32 sub_08016D30(u32);

u32 sub_08016D00(void)
{
    u8 acc = 0;
    u8 i;

    for (i = 0; i < 5; i++)
        acc |= sub_08016D30(gUnk_020232C0[i][0]);
    return acc;
}
