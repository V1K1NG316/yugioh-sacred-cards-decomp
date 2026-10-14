#include "global.h"

void sub_08003BC4(void);
void sub_08021E50(u16);
void sub_0801B334(void);
void sub_0801B41C(void);

extern u8 gUnk_020214D0[];

void sub_0801B2FC(void)
{
    switch (gUnk_020214D0[0x7EA]) {
    case 0:
        sub_0801B334();
        break;
    case 1:
        sub_0801B41C();
        break;
    default:
        sub_08021E50(0x37);
        sub_08003BC4();
        break;
    }
}
