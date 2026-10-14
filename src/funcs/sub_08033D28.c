#include "global.h"

void sub_08033CEC(u8 *);
void sub_08033D08(u8 *);

void sub_08033D28(u8 *p, u8 mode)
{
    switch (mode) {
    case 0:
        sub_08033CEC(p);
        break;
    case 1:
        sub_08033D08(p);
        break;
    }
}
