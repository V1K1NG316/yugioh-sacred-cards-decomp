#include "global.h"

extern u8 gUnk_02020DB0[];
extern u8 gUnk_080C8304[];

void sub_0801BFB8(void)
{
    u16 i;

    for (i = 0; i <= 0x384; i++)
        gUnk_02020DB0[i] = gUnk_080C8304[i];
}
