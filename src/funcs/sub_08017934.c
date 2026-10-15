#include "global.h"

void sub_08017934(u8 *src, u32 *dst, u16 colour)
{
    u8 i;
    u8 j;
    u32 w;

    for (i = 0; i <= 7; i++) {
        u8 bits = *src++;

        bits = bits << 1;

        w = 0;
        for (j = 0; j <= 7; j++) {
            w |= ((bits & 0x80) >> 7) << (j * 4);
            bits = bits << 1;
        }
        *dst++ = w;
    }
}
