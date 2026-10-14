#include "global.h"

extern u8 gUnk_02020C50[];

void sub_08005998(u32);
void sub_08014B28(void);
void sub_08014E74(void);
void sub_080151D0(void);
void sub_080157B8(u32);

void sub_080146D0(u32 n)
{
    switch ((u8)n) {
    case 0:
        sub_08005998(0);
        break;
    case 1:
        break;
    case 2:
        sub_08014B28();
        sub_08014E74();
        sub_080151D0();
        sub_080157B8(gUnk_02020C50[5]);
        sub_08005998(1);
        break;
    case 3:
        sub_08014E74();
    case 4:
        sub_080151D0();
    case 5:
        sub_08005998(3);
        break;
    case 6:
    case 7:
        sub_08014E74();
        sub_080151D0();
        sub_080157B8(gUnk_02020C50[5]);
        sub_08005998(3);
        break;
    }
}
