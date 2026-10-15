#include "global.h"

void sub_080243BC(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023284[];
extern u8 gUnk_02020C38[];

void sub_08028CBC(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023284;

    for (; i < 5; i++) {
        u16 *c = tab[i];

        if (*c != 0)
            sub_080243BC(c);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x3B, 0x3B);
        sub_08021E50(0x4A);
    }
}
