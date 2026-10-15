#include "global.h"

s8  sub_08035C30(u16);

extern u8  gUnk_020237D0[];
extern u32 gUnk_02023270[];

u32 sub_08035BEC(void)
{
    u8 i;

    gUnk_020237D0[5] = 0;

    for (i = 0; i <= 4; i++) {
        gUnk_020237D0[4] = i;

        if (sub_08035C30(*(u16 *)gUnk_02023270[i]) == 1)
            return 1;
    }

    return 0;
}
