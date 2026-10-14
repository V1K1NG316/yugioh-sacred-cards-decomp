#include "global.h"

extern u8 gUnk_02020C30[];
extern u32 gUnk_02023270[];
extern u8 gUnk_0201CB38[];
extern u8 gUnk_02020B00[];

void sub_08006BE4(u32);
void sub_0800D078(void);

void sub_0800ED58(void)
{
    u8 v = gUnk_02020C30[2];
    u8 hi = v >> 4;
    u8 lo = v & 0xF;

    do { } while (0); // matching: changes old_agbcc's register order (permuter)
    sub_08006BE4(*(u16 *)gUnk_02023270[hi * 5 + lo]);
    gUnk_0201CB38[0] = gUnk_02020B00[0x1A];
    sub_0800D078();
}
