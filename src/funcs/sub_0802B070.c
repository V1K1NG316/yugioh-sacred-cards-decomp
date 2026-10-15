/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023478[];
extern u8 gUnk_02020C38[];

void sub_080243A8(u32);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

void sub_0802B070(void)
{
    sub_080243A8(gUnk_02023270[gUnk_02023478[2] * 5 + gUnk_02023478[3]]);
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x36E, 0x36E);
        sub_08021E50(0x49);
    }
}
