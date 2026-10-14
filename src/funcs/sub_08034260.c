#include "global.h"

u32 sub_08034260(u8 *a, u8 *b)
{
    u8 i;
    u32 r = 10;

    for (i = 0; i <= 7; i++)
    {
        if (*a++ != *b++)
            r = 11;
    }
    return r;
}
