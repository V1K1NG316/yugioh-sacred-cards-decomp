#include "global.h"

extern u8 gUnk_02020C30[];
extern u32 gUnk_02023270[];

u8 sub_08026D38(u32);

u8 sub_08011A88(void)
{
    u8 r = 0;
    u8 v = gUnk_02020C30[2];
    u8 hi = v >> 4;
    u8 lo = v & 0xF;

    do { } while (0); // matching: changes old_agbcc's register order (permuter)
    if (sub_08026D38(gUnk_02023270[hi * 5 + lo]) == 1)
        r = 1;
    return r;
}
