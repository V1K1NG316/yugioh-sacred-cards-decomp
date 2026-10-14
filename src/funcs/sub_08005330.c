#include "global.h"

u8 sub_08004750(void);
void sub_08005368(void);
void sub_08005484(void);
void sub_08005580(void);
void sub_0800578C(void);

void sub_08005330(void)
{
    switch (sub_08004750()) {
    case 1:
        sub_08005484();
        break;
    case 2:
        sub_08005580();
        break;
    case 3:
        sub_0800578C();
        break;
    case 0:
    default:
        sub_08005368();
        break;
    }
}
