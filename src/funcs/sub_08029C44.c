#include "global.h"

u32 sub_0803691C(void);
void sub_08023998(u32);
void sub_080239E0(u32);
void sub_0802321C(void);
void sub_08023614(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u16 gUnk_0202347C[];
extern u8 gUnk_02020C38[];

void sub_08029C44(void)
{

    if (sub_0803691C() == 0) {
        u16 *p = gUnk_0202347C;

        sub_080239E0(p[0] - 1);
        sub_0802321C();
        p[0] = 1;
    } else {
        u16 *p = gUnk_0202347C;

        sub_08023998(p[1] - 1);
        sub_0802321C();
        p[1] = 1;
    }
    sub_08023614();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x342, 0x342);
        sub_08021E50(0x58);
    }
}
