#include "global.h"

void sub_0803692C(u32, u32, u32);
void sub_08036934(u32, u32, u32);

extern u8 gUnk_080BA2E4[];
extern u8 gUnk_080BC2E4[];
extern u8 gUnk_080BE2E4[];
extern u8 gUnk_080BE364[];
extern u8 gUnk_080BEC5C[];
extern u8 gUnk_080BE994[];
extern u8 gUnk_080BE814[];
extern u8 gUnk_02000400[];
extern u8 gUnk_02000000[];
extern u8 gUnk_0200FC00[];
extern u8 gUnk_02000200[];

void sub_08018C0C(void)
{
    u32 i;

    sub_0803692C((u32)gUnk_080BA2E4, (u32)gUnk_02000400, 0x04000800);
    sub_0803692C((u32)gUnk_080BC2E4, (u32)gUnk_02000400 + 0x2000, 0x04000800);
    sub_0803692C((u32)gUnk_080BE2E4, (u32)gUnk_02000000, 0x04000020);

    for (i = 0; i <= 0x13; i++)
        sub_0803692C((u32)(gUnk_080BE364 + i * 0x3C), (u32)(gUnk_0200FC00 + i * 0x40),
                     0x0400000F);

    sub_08036934((u32)gUnk_080BEC5C, (u32)(gUnk_0200FC00 + 0x800), 0x800);
    sub_0803692C((u32)gUnk_080BE994, (u32)gUnk_02000200, 0x04000018);
    sub_0803692C((u32)gUnk_080BE814, (u32)gUnk_02000200 + 0x60, 0x04000010);
}
