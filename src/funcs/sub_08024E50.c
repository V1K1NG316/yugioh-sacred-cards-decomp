#include "global.h"

extern u8 gUnk_02008BA0[];
extern u8 gUnk_04000740[];
extern u8 gUnk_04000120[];
extern u8 gUnk_060087A0[];
extern u8 gUnk_0600E800[];

void sub_0803692C(u32, u32, u32);

void sub_08024E50(void)
{
    u8 *p = gUnk_02008BA0;

    sub_0803692C((u32)p, (u32)gUnk_060087A0, (u32)gUnk_04000740);
    p += 0x6060;
    sub_0803692C((u32)p, (u32)gUnk_0600E800, (u32)gUnk_04000120);
}
