#include "global.h"

u32 sub_0803691C(void);
void sub_08023974(u16);
void sub_080239BC(u16);
void sub_0802321C(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020C38[];

void sub_0802867C(void)
{
    if (sub_0803691C() == 0)
        sub_08023974(1000);
    else
        sub_080239BC(1000);
    sub_0802321C();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x16B, 0x16B);
        sub_08021E50(0x4E);
    }
}
