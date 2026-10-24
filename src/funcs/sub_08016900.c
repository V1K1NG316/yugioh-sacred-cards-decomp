/* compiler: agbcc (A37) */
#include "global.h"

extern u16 gUnk_02020CB0[];

void sub_08016900(void)
{
    u32 i;

    gUnk_02020CB0[0] = 0;
    gUnk_02020CB0[1] = 0;
    for (i = 0; i <= 0x18; i++) {
        gUnk_02020CB0[2 + i * 2] = 0;
        gUnk_02020CB0[3 + i * 2] = 0;
    }
}
