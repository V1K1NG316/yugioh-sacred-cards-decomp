#include "global.h"

void sub_08024980(u8);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023160[];
extern u8 gUnk_02020C38[];

void sub_08028E00(void)
{
    gUnk_02023160[0xF0] = 3;
    if (gUnk_02020C38[0] == 0) {
        sub_08024980(3);
        sub_08024F64(0x20D, 0x20D);
        sub_08021E50(0x4f);
    }
}
