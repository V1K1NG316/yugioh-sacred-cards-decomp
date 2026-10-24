#include "global.h"

void sub_08014554(u32 a)
{
    u32 *p = (u32 *)0x02020C50;

    if (a > *p)
        *p = 0;
    else
        *p -= a;
}
