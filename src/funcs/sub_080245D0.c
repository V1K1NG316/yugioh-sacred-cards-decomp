#include "global.h"

void sub_080245D0(u8 *dst, u8 *src)
{
    u8 row;

    for (row = 0; row < 4; row++) {
        u8 col;

        for (col = 0; col < 4; col++) {
            u8 i;

            for (i = 0; i < 0x20; i++)
                *dst++ = *src++;
        }
        dst += 0x380;
    }
}
