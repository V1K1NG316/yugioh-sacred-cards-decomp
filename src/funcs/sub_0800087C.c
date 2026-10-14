#include "global.h"

void sub_08028438(void);
void sub_080284A0(void);

extern u16 gUnk_02023474;
extern u16 gUnk_0202344C;
extern u16 gUnk_02023458;
extern u16 gUnk_0202345C;
extern u16 gUnk_02023468;

void sub_0800087C(void)
{
    *(u16 *)0x0400000C = 0x9D02;
    *(u16 *)0x0400000E = 0x1F09;
    *(u16 *)0x04000208 = 1;
    *(u16 *)0x04000200 = 1;
    *(u16 *)0x04000004 = 8;
    *(u16 *)0x04000000 = 0x2C00;
    gUnk_02023474 = 0;
    gUnk_0202344C = 0xFFB0;
    gUnk_02023458 = 0xFFDC;
    sub_08028438();
    *(u16 *)0x04000040 = 0x30E8;
    *(u16 *)0x04000044 = 0x248C;
    *(u8 *)0x04000048 = 0x2C;
    *(u8 *)0x0400004A = 4;
    gUnk_0202345C = 0x3F48;
    gUnk_02023468 = 0x1000;
    sub_080284A0();
}
