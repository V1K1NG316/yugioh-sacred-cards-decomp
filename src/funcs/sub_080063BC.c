#include "global.h"

extern u32 gUnk_020237DC[];

u32 sub_08038E30(u32, u32, u32, u32);

u8 sub_080063BC(void)
{
    u8 v;

    sub_08038E30(0x0E000000, (u32)&v, 1, gUnk_020237DC[0]);
    return v;
}
