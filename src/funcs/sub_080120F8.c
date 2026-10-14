#include "global.h"

extern u8 gUnk_02020C30[];
extern u8 gUnk_020237D0[];
extern u32 gUnk_02023270[];

u8 sub_08026DDC(u32);
u32 sub_08035BEC(void);

u32 sub_080120F8(void)
{
    u8 row = gUnk_02020C30[2] >> 4;
    u8 col = gUnk_02020C30[2] & 0xF;

    if (sub_08026DDC(gUnk_02023270[row * 5 + col]) == 1) {
        gUnk_020237D0[2] = row;
        gUnk_020237D0[3] = col;
        *(u16 *)gUnk_020237D0 = *(u16 *)gUnk_02023270[row * 5 + col];
        if (sub_08035BEC() != 1)
            return 1;
    }
    return 0;
}
