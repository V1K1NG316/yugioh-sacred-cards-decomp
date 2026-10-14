#include "global.h"

extern u8 gUnk_02020D88[];

void sub_080181CC(void)
{
    u8 i;

    for (i = 0; i < 2; i++)
        if (gUnk_02020D88[i] == 0)
            gUnk_02020D88[i] = 1;
}
