#include "global.h"

extern u8 gUnk_02020C30[];
extern u32 gUnk_02023270[];

u8 sub_08026D98(u32);
s32 sub_08023114(u16);

u32 sub_08011ED8(void)
{
    u8 row = gUnk_02020C30[2] >> 4;
    u8 col = gUnk_02020C30[2] & 0xF;

    if (sub_08026D98(gUnk_02023270[row * 5 + col]) == 1 &&
        sub_08023114(*(u16 *)gUnk_02023270[row * 5 + col]) <= 0)
        return 1;
    return 0;
}
