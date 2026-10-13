#include "global.h"

extern u8 gUnk_02020B00[];

u32 sub_0801A624(u32);
void sub_0801715C(u32, u32, u32);

void sub_080073A8(void)
{
    sub_0801715C(0x02005000, sub_0801A624(gUnk_02020B00[0x17]), 0x901);
}
