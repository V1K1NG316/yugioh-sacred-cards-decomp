#include "global.h"

u8 *sub_08036A00(u8 *a, u8 *b, u32 n)
{
    s32 i;

    i = n - 1;
    if (n != 0) {
        do {
            if (*b++ != *a++) {
                return b - 1;
            }
        } while (--i != -1);
    }
    return NULL;
}
