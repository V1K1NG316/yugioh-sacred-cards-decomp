#include "global.h"

void sub_080059DC(void);
void sub_08005A00(void);
void sub_08005A70(void);
void sub_08005A74(void);

void sub_08005998(u8 a)
{
    switch (a) {
    case 0:
        sub_080059DC();
        break;
    case 1:
        sub_08005A00();
        sub_08005A70();
        sub_08005A74();
        break;
    case 2:
        sub_08005A70();
        break;
    case 3:
        sub_08005A70();
        break;
    }
}
