#include "global.h"

extern u8 gUnk_020000A0[];
extern u8 gUnk_02008440[];
extern u8 gUnk_040001D0[];
extern u8 gUnk_050000A0[];
extern u8 gUnk_06008040[];

void sub_08028438(void);
void sub_080284CC(void);
void sub_0803692C(u32, u32, u32);

void sub_08024E18(void)
{
    sub_080284CC();
    sub_08028438();
    sub_0803692C((u32)gUnk_02008440, (u32)gUnk_06008040, (u32)gUnk_040001D0);
    sub_0803692C((u32)gUnk_020000A0, (u32)gUnk_050000A0, 0x20);
}
