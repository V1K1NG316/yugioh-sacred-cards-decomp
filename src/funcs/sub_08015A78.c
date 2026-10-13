#include "global.h"

extern u8 gUnk_02020C50[];

void sub_08021E50(u16);
void sub_08014630(u8);

void sub_08015A78(void)
{
    sub_08021E50(0x37);
    if (gUnk_02020C50[7] <= 8) {
        gUnk_02020C50[5] = gUnk_02020C50[7];
        sub_08014630(gUnk_02020C50[5]);
    }
}
