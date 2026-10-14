#include "global.h"

u32 sub_0803691C(void);
void sub_080239E0(u16);
void sub_08023998(u16);
void sub_0802321C(void);
void sub_08023614(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020C38[];

void sub_08029260(void)
{
    if (sub_0803691C() == 0)
        sub_080239E0(0x32);
    else
        sub_08023998(0x32);
    sub_0802321C();
    sub_08023614();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x9a, 0x9a);
        sub_08021E50(0x4d);
    }
}
