#include "global.h"

void sub_0803692C(u32, u32, u32);
void sub_0801715C(u32, u8 *, u32);

extern u8 gUnk_02008400[];
extern u8 gUnk_020085E0[];
extern u8 gUnk_02020B00[];

void sub_080259D4(void)
{
    u8 buf[0x20];
    u8 i;

    for (i = 0; i <= 0xE; i++)
        sub_0803692C((u32)gUnk_02008400, (u32)(gUnk_02008400 + 0x1E0 + i * 0x20), 0x10);
    for (i = 0; i <= 0x1D; i++)
        buf[i] = *(u8 *)(*(u32 *)gUnk_02020B00 + i);
    buf[i] = 0;
    sub_0801715C((u32)gUnk_020085E0, buf, 0x801);
}
