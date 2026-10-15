/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u32 gUnk_02023284[];
extern u32 gUnk_02023298[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

u32  sub_08018D68(u16);
void sub_08028308(u32, u32);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802BD00(void)
{
    u8 i;

    for (i = 0; i <= 4; i++) {
        if (sub_08018D68(*(u16 *)gUnk_02023284[i]) == 0)
            sub_08028308(gUnk_02023284[i], 1);
    }
    for (i = 0; i <= 4; i++) {
        if (sub_08018D68(*(u16 *)gUnk_02023298[i]) == 0)
            sub_08028308(gUnk_02023298[i], 0);
    }
    sub_08028308(gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x150);
        sub_08021E50(0x4B);
    }
}
