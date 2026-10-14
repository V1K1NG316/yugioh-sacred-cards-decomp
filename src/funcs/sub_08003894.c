#include "global.h"

void sub_08028438(void);
void sub_080284A0(void);

extern u16 gUnk_02023474;
extern u16 gUnk_02023450;
extern u16 gUnk_0202344C;
extern u16 gUnk_02023458;
extern u16 gUnk_0202345C;
extern u16 gUnk_02023464;

void sub_08003894(void)
{
    *(u16 *)0x0400000C = 0x1F0E;
    *(u16 *)0x0400000E = 0x1E03;
    *(u16 *)0x04000208 = 1;
    *(u16 *)0x04000200 = 1;
    *(u16 *)0x04000004 = 8;
    *(u16 *)0x04000000 = 0x6C00;
    gUnk_02023474 = 0;
    gUnk_02023450 = 0;
    gUnk_0202344C = 0;
    gUnk_02023458 = 0;
    sub_08028438();
    *(u16 *)0x04000040 = 0x08C7;
    *(u16 *)0x04000044 = 0x084F;
    *(u16 *)0x04000042 = 0x08EF;
    *(u16 *)0x04000046 = 0x7F97;
    *(u8 *)0x04000048 = 8;
    *(u8 *)0x04000049 = 8;
    *(u8 *)0x0400004A = 8;
    gUnk_0202345C = 0xE8;
    gUnk_02023464 = 6;
    sub_080284A0();
}
