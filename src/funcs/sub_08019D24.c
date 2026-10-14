#include "global.h"

extern u8 gUnk_02020DA8[];

u32 sub_08019D24(void)
{
    u8 v = gUnk_02020DA8[0];
    u8 c = 0;
    u8 i;

    for (i = 0; i <= 5; i++) {
        if (v & 1)
            c++;
        v >>= 1;
    }
    return c;
}
