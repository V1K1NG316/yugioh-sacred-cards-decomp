#include "global.h"

void sub_08026788(void);
void sub_0801715C(u32, u32, u32);
void sub_08003BC4(void);
void sub_08024E8C(void);

extern u8 gUnk_02008BA0[];
extern u16 gUnk_02023454[];
extern u16 gUnk_0202346C[];
extern u16 gUnk_02023474[];
extern u16 gUnk_02023450[];

void sub_08026704(void)
{
    sub_08026788();
    sub_0801715C((u32)gUnk_02008BA0, 0x08D4C650, 0x801);
    *(u16 *)0x04000008 = 0x9E08;
    gUnk_02023454[0] = gUnk_02023474[0];
    gUnk_0202346C[0] = gUnk_02023450[0];
    sub_08003BC4();
    sub_08024E8C();
    *(u16 *)0x04000000 = 0x7700;
    *(u16 *)0x04000042 = 0xF0;
    *(u16 *)0x04000046 = 0x98;
    *(u8 *)0x04000049 = 0x35;
    *(u16 *)0x04000054 = 7;
    *(u16 *)0x0400004A = 0x1E;
}
