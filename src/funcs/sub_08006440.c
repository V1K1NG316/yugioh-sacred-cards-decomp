#include "global.h"

void sub_080061F4(void);
u16 sub_08021F28(void);
u16 sub_0800648C(void);

u32 sub_08006440(void)
{
    u16 a;
    u16 b;
    u32 r = 0;

    sub_080061F4();
    a = sub_08021F28();
    b = sub_0800648C();
    if (a == b)
        r = 1;
    return r;
}
