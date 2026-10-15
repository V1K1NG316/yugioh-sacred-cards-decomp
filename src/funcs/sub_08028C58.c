#include "global.h"

void sub_080243A8(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023298[];
extern u8 gUnk_02020C38[];

void sub_08028C58(void)
{
    u8 i = 0;
    u16 **tab = (u16 **)gUnk_02023298;
    register u16 *c asm("r1");   /* FAKEMATCH: slot pointer in r1 */

    for (; i < 5; i++) {
        c = tab[i];

        if (*c == 0x60)
            sub_080243A8(c);

        c = tab[i];

        if (*c == 0x61)
            sub_080243A8(c);

        c = tab[i];

        if (*c == 0x62)
            sub_080243A8(c);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(99, 99);
        sub_08021E50(0x49);
    }
}
