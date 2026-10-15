#include "global.h"

void sub_0803692C(u32, u32, u32);
void sub_08036934(u32, u32);

extern u8 gUnk_080CA618[];
extern u8 gUnk_080CADB4[];
extern u8 gUnk_080CAE14[];
extern u8 gUnk_0200C400[];
extern u8 gUnk_0200BC00[];
extern u8 gUnk_020001A0[];
extern u16 gUnk_02023458[];
extern u16 gUnk_0202344C[];

void sub_0801E15C(void)
{
    u8 i;

    gUnk_02023458[0] = 0;
    gUnk_0202344C[0] = 0;
    sub_08036934((u32)gUnk_080CA618, (u32)gUnk_0200C400);
    sub_0803692C((u32)gUnk_080CADB4, (u32)gUnk_020001A0, 0x30);
    for (i = 0; i <= 0x13; i++)
        sub_0803692C((u32)(gUnk_080CAE14 + i * 0x3C), (u32)(gUnk_0200BC00 + i * 0x40), 0x1E);
}
