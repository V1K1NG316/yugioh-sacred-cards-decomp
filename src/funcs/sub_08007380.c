#include "global.h"

extern u8 gUnk_02020B00[];

u32 sub_0802319C(u32);
void sub_0801715C(u32, u32, u32);

void sub_08007380(void)
{
    sub_0801715C(0x02004C80, sub_0802319C(gUnk_02020B00[0x16]), 0x901);
}
