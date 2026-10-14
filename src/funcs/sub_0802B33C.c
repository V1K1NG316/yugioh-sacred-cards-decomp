#include "global.h"

void sub_08006BE4(u16);
void sub_08038E24(u32);

extern u16 gUnk_02023480[];
extern u8 gUnk_02020B00[];
extern u32 gUnk_080FB900[];

void sub_0802B33C(void)
{
    sub_08006BE4(gUnk_02023480[0]);
    sub_08038E24(gUnk_080FB900[gUnk_02020B00[0x1A]]);
}
