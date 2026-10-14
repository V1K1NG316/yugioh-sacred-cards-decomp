#include "global.h"

extern u8 gUnk_02008BA0[];
extern u8 gUnk_04000058[];
extern u8 gUnk_04000400[];
extern u8 gUnk_060087A0[];
extern u8 gUnk_0600F000[];

void sub_08028438(void);
void sub_0803692C(u32, u32, u32);

void sub_08024E8C(void)
{
    u8 *p;

    sub_08028438();
    p = gUnk_02008BA0;
    sub_0803692C((u32)p, (u32)gUnk_060087A0, (u32)gUnk_04000058);
    p += 0x6860;
    sub_0803692C((u32)p, (u32)gUnk_0600F000, (u32)gUnk_04000400);
}
