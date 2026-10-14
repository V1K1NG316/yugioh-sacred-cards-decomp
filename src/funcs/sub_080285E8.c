#include "global.h"

void sub_08006BE4(u16);
void sub_08038E24(u32);

extern u16 gUnk_02023478[];
extern u32 gUnk_080FB79C[];
extern u8 gUnk_02020B00[];

void sub_080285E8(void)
{
    sub_08006BE4(gUnk_02023478[0]);
    sub_08038E24(gUnk_080FB79C[gUnk_02020B00[0x1B]]);
}
