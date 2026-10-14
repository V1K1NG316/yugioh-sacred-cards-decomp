#include "global.h"

void sub_08024980(u8);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023160[];
extern u8 gUnk_02020C38[];

void sub_08028B80(void)
{
    gUnk_02023160[0xF0] = 0;
    if (gUnk_02020C38[0] == 0) {
        sub_08024980(0);
        sub_08024F64(0x4a, 0x4a);
        sub_08021E50(0x4f);
    }
}
