#include "global.h"

u32 sub_0803691C(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020C38[];

void sub_0802AA4C(void)
{
    sub_0803691C();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x35E, 0x35E);
        sub_08021E50(0x3b);
    }
}
