#include "global.h"

u32 sub_0803691C(void);
void sub_08023974(u16);
void sub_080239BC(u16);
void sub_0802321C(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020C38[];

void sub_08029220(void)
{
    if (sub_0803691C() == 0)
        sub_08023974(0x1F4);
    else
        sub_080239BC(0x1F4);
    sub_0802321C();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x264, 0x264);
        sub_08021E50(0x4e);
    }
}
