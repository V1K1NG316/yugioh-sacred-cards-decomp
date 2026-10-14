#include "global.h"

extern u8 gUnk_02020DB0[];
extern u8 gUnk_02021140[];
extern u8 gUnk_02020770[];
extern u8 gUnk_02021CC0[];

void sub_0801B85C(void)
{
    u16 i;

    for (i = 0; i <= 0x384; i++) {
        gUnk_02020DB0[i] = gUnk_02021140[i];
        gUnk_02020770[i] = gUnk_02021CC0[i];
    }
}
