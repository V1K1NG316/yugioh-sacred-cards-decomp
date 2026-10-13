#include "global.h"

void sub_080061C8(void);
u16 sub_08021F28(void);
u16 sub_08006468(void);

u32 sub_08006418(void)
{
    u16 a;
    u16 b;
    u32 r = 0;

    sub_080061C8();
    a = sub_08021F28();
    b = sub_08006468();
    if (a == b)
        r = 1;
    return r;
}
