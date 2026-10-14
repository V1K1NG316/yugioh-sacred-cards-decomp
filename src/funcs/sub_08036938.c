#include "global.h"

void sub_08036938(u8 *src, u8 *dst, u32 n)
{
    s32 i;

    i = n - 1;
    if (n != 0) {
        do {
            *dst++ = *src++;
        } while (--i != -1);
    }
}
