#include "global.h"

extern u32 gUnk_02020DA0[];

u32 sub_08019C34(unsigned long long a)
{
    unsigned long long *p = (unsigned long long *)gUnk_02020DA0;

    if (a > *p)
        return 0;
    return 1;
}
