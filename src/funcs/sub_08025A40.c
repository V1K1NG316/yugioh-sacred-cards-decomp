#include "global.h"

void sub_080042CC(u32);
void sub_08008ECC(u8, u32);
void sub_08017088(u32, u32, u32);
void sub_0803692C(u32, u32, u32);

extern u8 gUnk_02020B00[];
extern u8 gUnk_02008400[];
extern u8 gUnk_02008440[];
extern u8 gUnk_02020C00[];
extern u8 gUnk_08D4C2D0[];

void sub_08025A40(void)
{
    u8 i;

    if (gUnk_02020B00[0x18] != 0) {
        sub_080042CC((u32)gUnk_02008440);
        sub_08008ECC(gUnk_02020B00[0x18], 1);
        for (i = 0; i <= 1; i++)
            sub_08017088((i + 1) * 0x20 + (u32)gUnk_02008440,
                         *(u16 *)((u8 *)gUnk_08D4C2D0 + gUnk_02020C00[i] * 2), 0x801);
    } else {
        sub_0803692C((u32)gUnk_02008400, (u32)(gUnk_02008400 + 0x40), 0x10);
        sub_0803692C((u32)gUnk_02008400, (u32)(gUnk_02008400 + 0x60), 0x10);
        sub_0803692C((u32)gUnk_02008400, (u32)(gUnk_02008400 + 0x80), 0x10);
    }
}
