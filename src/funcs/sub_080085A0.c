#include "global.h"

u8 sub_08004750(void);
void sub_080085D8(void);
void sub_080086F4(void);
void sub_080087F0(void);
void sub_080089FC(void);

void sub_080085A0(void)
{
    switch (sub_08004750()) {
    case 1:
        sub_080086F4();
        break;
    case 2:
        sub_080087F0();
        break;
    case 3:
        sub_080089FC();
        break;
    case 0:
    default:
        sub_080085D8();
        break;
    }
}
