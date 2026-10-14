#include "global.h"

extern u8 gUnk_02020C50[];

void sub_08014630(u32);

void sub_08014678(void)
{
    gUnk_02020C50[5]++;
    if (gUnk_02020C50[5] > 8)
        gUnk_02020C50[5] = 0;
    sub_08014630(gUnk_02020C50[5]);
}
