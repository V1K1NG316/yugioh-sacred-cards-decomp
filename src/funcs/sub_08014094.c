#include "global.h"

extern u32 gUnk_02020C3C[];

void sub_080140EC(void);

void sub_08014094(u32 n)
{
    u32 v = gUnk_02020C3C[0];

    if (n > 0x1869F - v)
        gUnk_02020C3C[0] = 0x1869F;
    else
        gUnk_02020C3C[0] = v + n;
    sub_080140EC();
}
