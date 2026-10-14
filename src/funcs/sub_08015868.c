#include "global.h"

u32 sub_08015868(u16 v, u16 *p)
{
    u16 i = 0;

    while (p[i] != 0)
    {
        if (p[i] == v)
            return 1;
        i++;
    }
    return 0;
}
