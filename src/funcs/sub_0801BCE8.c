#include "global.h"

void sub_08003BC4(void);
void sub_08021E50(u16);
void sub_0801BD20(void);
void sub_0801BE28(void);

extern u8 gUnk_020214D0[];

void sub_0801BCE8(void)
{
    switch (gUnk_020214D0[0x7EA]) {
    case 0:
        sub_0801BD20();
        break;
    case 1:
        sub_0801BE28();
        break;
    default:
        sub_08021E50(0x37);
        sub_08003BC4();
        break;
    }
}
