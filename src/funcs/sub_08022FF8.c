#include "global.h"

extern u8 gUnk_02000000[];

void sub_0803692C(u32, u32, u32);

void sub_08022FF8(void)
{
    u16 v;
    u16 *p = &v;

    v = 0;
    sub_0803692C((u32)p, (u32)gUnk_02000000, 0x01000100);
}
