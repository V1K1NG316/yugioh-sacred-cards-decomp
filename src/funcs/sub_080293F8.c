#include "global.h"

void sub_080243A8(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023298[];
extern u8 gUnk_02020C38[];

void sub_080293F8(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023298;
    register u16 *c asm("r1");   /* FAKEMATCH: the ROM keeps the slot pointer in r1 across the loop */

    for (; i < 5; i++) {
        c = tab[i];

        if (*c == 0x22A)
            sub_080243A8(c);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x0C, 0x22A);
        sub_08021E50(0x49);
    }
}
