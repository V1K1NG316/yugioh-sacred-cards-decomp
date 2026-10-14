#include "global.h"

extern u16 gUnk_02020C5A[];

u8 sub_0801457C(u16 a)
{
    u8 count = 0;
    u8 i;

    for (i = 0; i <= 0x27; i++) {
        if (gUnk_02020C5A[i] == a)
            count++;
    }
    return count;
}
