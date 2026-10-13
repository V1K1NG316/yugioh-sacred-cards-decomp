#include "global.h"

extern u8 gUnk_02020C50[];

u8 sub_080144C8(u8 a)
{
    if (gUnk_02020C50[8] < a) {
        a = gUnk_02020C50[8];
        gUnk_02020C50[8] = 0;
    } else {
        gUnk_02020C50[8] -= a;
    }
    return a;
}
