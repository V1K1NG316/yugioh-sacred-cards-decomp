#include "global.h"

extern u32 gUnk_020237DC[];

u32 sub_08038E30(u32, u32, u32, u32);

u16 sub_0800648C(void)
{
    u16 v;

    sub_08038E30(0x0E007FFE, (u32)&v, 2, gUnk_020237DC[0]);
    return v;
}
