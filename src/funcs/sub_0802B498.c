/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];
extern u8 gUnk_02023160[];

void sub_08028308(u32, u32);
void sub_08024980(u8);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802B498(void)
{
    u32 base = (u32)gUnk_02023160;
    u8 *p = (u8 *)base;

    p += 0xF0;
    *p = 4;
    sub_08028308(gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08024980(*p);
        sub_08021E50(0x41);
        sub_08024F64(0x14D);
        sub_08021E50(0x4F);
    }
}
