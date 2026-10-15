#include "global.h"

void sub_08006BE4(u16);
void sub_080243A8(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020B00[];
extern u8 gUnk_02023298[];
extern u8 gUnk_02023478[];
extern u8 gUnk_02020C38[];

void sub_080290DC(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023298;

    for (; i < 5; i++) {
        sub_08006BE4(*tab[i]);

        if (gUnk_02020B00[0x16] == 0x14)
            sub_080243A8(tab[(u8)gUnk_02023478[3]]);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0xEB, 0xEB);
        sub_08021E50(0x49);
    }
}
