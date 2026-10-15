/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023478[];
extern u8 gUnk_02023160[];
extern u16 gUnk_02020B00[];
extern u8 gUnk_02020C38[];

void sub_08006BD0(u8, s8);
void sub_08006CB4(u16);
u32  sub_0803691C(void);
void sub_080239E0(u16);
void sub_08023998(u16);
void sub_0802321C(void);
void sub_08023614(void);
void sub_080243BC(u32);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

void sub_0802B218(void)
{
    u8 v = gUnk_02023160[0xF0];

    sub_08006BD0(v, *(s8 *)(gUnk_02023270[gUnk_02023478[2] * 5 + gUnk_02023478[3]] + 2));
    sub_08006CB4(*(u16 *)gUnk_02023270[gUnk_02023478[2] * 5 + gUnk_02023478[3]]);
    if (sub_0803691C() == 0)
        sub_080239E0(gUnk_02020B00[9]);
    else
        sub_08023998(gUnk_02020B00[9]);
    sub_0802321C();
    sub_08023614();
    sub_080243BC(gUnk_02023270[gUnk_02023478[2] * 5 + gUnk_02023478[3]]);
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x36D, 0x36D);
        sub_08021E50(0x45);
    }
}
