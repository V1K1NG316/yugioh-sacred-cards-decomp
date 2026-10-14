#include "global.h"

extern u8 gUnk_02020C50[];

void sub_08021E50(u32);

void sub_08014294(void)
{
    gUnk_02020C50[6]++;
    if (gUnk_02020C50[6] > 3)
        gUnk_02020C50[6] = 0;
    sub_08021E50(0x36);
}
