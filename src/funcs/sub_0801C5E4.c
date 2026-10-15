#include "global.h"

void sub_0803692C(u32, u32, u32);

extern u8 gUnk_080C86E8[];
extern u8 gUnk_080C8B98[];
extern u8 gUnk_080C9048[];
extern u8 gUnk_0200A400[];
extern u8 gUnk_0200AC00[];
extern u8 gUnk_0200B400[];
extern u16 gUnk_0202346C[];
extern u16 gUnk_02023454[];

void sub_0801C5E4(void)
{
    u8 i;

    gUnk_0202346C[0] = 0;
    gUnk_02023454[0] = 0;
    for (i = 0; i <= 0x13; i++)
        sub_0803692C((u32)(gUnk_080C86E8 + i * 0x3C), (u32)(gUnk_0200A400 + i * 0x40), 0x1E);
    for (i = 0; i <= 0x13; i++)
        sub_0803692C((u32)(gUnk_080C8B98 + i * 0x3C), (u32)(gUnk_0200AC00 + i * 0x40), 0x1E);
    for (i = 0; i <= 0x13; i++)
        sub_0803692C((u32)(gUnk_080C9048 + i * 0x3C), (u32)(gUnk_0200B400 + i * 0x40), 0x1E);
}
