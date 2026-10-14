#include "global.h"

extern u32 gUnk_02020DA0[];

u32 sub_08019BFC(unsigned long long a)
{
    unsigned long long *p = (unsigned long long *)gUnk_02020DA0;

    if (a > 0x9184E729FFFULL - *p)
        return 0;
    return 1;
}
