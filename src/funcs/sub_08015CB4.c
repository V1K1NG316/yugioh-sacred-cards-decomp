#include "global.h"

extern u16 gUnk_0202344C[];
extern u16 gUnk_02023450[];
extern u16 gUnk_02023454[];
extern u16 gUnk_02023458[];
extern u16 gUnk_02023460[];
extern u16 gUnk_0202346C[];
extern u16 gUnk_02023470[];
extern u16 gUnk_02023474[];

void sub_08015C5C(void);
void sub_08028438(void);
void sub_080285D8(void);

void sub_08015CB4(void)
{
    sub_080285D8();
    sub_08015C5C();
    *(u16 *)0x04000008 = 0x0F04;
    *(u16 *)0x0400000A = 0x1F0D;
    *(u16 *)0x0400000C = 0x170A;
    *(u16 *)0x0400000E = 0x0703;
    gUnk_0202346C[0] = 0;
    gUnk_02023454[0] = 0;
    gUnk_02023460[0] = 0xF8;
    gUnk_02023470[0] = 0;
    gUnk_02023450[0] = 0xFD;
    gUnk_02023474[0] = 4;
    gUnk_02023458[0] = 0;
    gUnk_0202344C[0] = 0;
    sub_08028438();
}
