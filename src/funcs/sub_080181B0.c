#include "global.h"

extern u8 gUnk_02020D88[];

void sub_080181B0(void)
{
    u8 i;

    for (i = 0; i < 2; i++)
        gUnk_02020D88[i] = 0;
}
