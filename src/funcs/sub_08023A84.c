#include "global.h"

extern u8 gUnk_02023120[];

u8 sub_08023A04(u8, u8);
void sub_08023B88(void);
void sub_08023B9C(void);

u8 sub_08023A84(void)
{
    u8 v = sub_08023A04(gUnk_02023120[8], gUnk_02023120[0x14]);

    switch (v) {
    case 0:
        sub_08023B88();
        break;
    case 1:
        break;
    case 2:
        sub_08023B9C();
        break;
    }
    return v;
}
