#include "global.h"

void sub_080243A8(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);
u32 sub_0803691C(void);
void sub_08023998(u16);
void sub_080239E0(u16);
void sub_0802321C(void);
void sub_08023614(void);

extern u8 gUnk_02023298[];
extern u8 gUnk_02020C38[];

void sub_08029624(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023298;
    register u16 *c asm("r1");   /* FAKEMATCH: the ROM keeps the slot pointer in r1 across the loop */

    for (; i < 5; i++) {
        c = tab[i];

        if (*c != 0)
            sub_080243A8(c);
    }
    if (sub_0803691C() == 0)
        sub_08023998(1000);
    else
        sub_080239E0(1000);
    sub_0802321C();
    sub_08023614();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0xE5, 0xE5);
        sub_08021E50(0x49);
    }
}
