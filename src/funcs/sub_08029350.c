#include "global.h"

void sub_080243A8(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023364[];
extern u8 gUnk_02020C38[];

void sub_08029350(void)
{
    u8 i = 0;
    u8 *flag = gUnk_02020C38;
    u16 **tab = (u16 **)gUnk_02023364;
    register u16 *c asm("r1");   /* FAKEMATCH: the ROM keeps the slot pointer in r1 across the loop */

    for (; i < 5; i++) {
        c = tab[i];

        if (*c != 0)
            *(u8 *)(c + 2) |= 0x10;
    }
    if (*flag == 0) {
        sub_08024F64(0x192, 0x192);
        sub_08021E50(0x3C);
    }
}
