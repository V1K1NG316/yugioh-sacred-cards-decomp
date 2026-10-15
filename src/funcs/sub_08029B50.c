#include "global.h"

void sub_08028308(u16 *, u8);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);
u32 sub_0803691C(void);
void sub_08023998(u16);
void sub_080239E0(u16);
void sub_0802321C(void);
void sub_08023614(void);

extern u8 gUnk_02023284[];
extern u8 gUnk_02020C38[];

void sub_08029B50(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023284;

    for (; i < 5; i++) {
        u16 *c = tab[i];

        sub_08028308(c, 1);
    }
    if (sub_0803691C() == 0)
        sub_080239E0(4000);
    else
        sub_08023998(4000);
    sub_0802321C();
    sub_08023614();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x340, 0x340);
        sub_08021E50(0x56);
    }
}
