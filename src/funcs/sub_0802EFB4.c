/* compiler: agbcc (A37) */
#include "global.h"

void sub_08006BE4(u16);
void sub_08028308(u16 *, u16);
void sub_08021E50(u16);
void sub_08024F64(u16);

extern u32 gUnk_02023284[];
extern u8 gUnk_02020B00[];
extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

void sub_0802EFB4(void)
{
    u8 i = 0;
    u32 *base = gUnk_02023284;

    for (; i <= 4; i++) {
        sub_08006BE4(*(u16 *)base[i]);
        if (gUnk_02020B00[0x16] == 0xa)
            sub_08028308((u16 *)base[i], 1);
    }
    sub_08028308((u16 *)gUnk_02023270[(u8)gUnk_02023480[2] * 5 + (u8)gUnk_02023480[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x296);
        sub_08021E50(0x4C);
    }
}
