#include "global.h"

extern u8 gUnk_02020C30[];
extern u32 gUnk_02023270[];

void sub_08028308(u32, u32);

void sub_08009250(void)
{
    u8 v = gUnk_02020C30[2];
    u8 hi = v >> 4;
    u8 lo = v & 0xF;

    do { } while (0); // matching: changes old_agbcc's register order (permuter)
    sub_08028308(gUnk_02023270[hi * 5 + lo], 0);
}
