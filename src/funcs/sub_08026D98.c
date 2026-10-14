#include "global.h"

u32 sub_08023C34(u16);

u32 sub_08026D98(u16 *p)
{
    u32 r = 0;

    if (*p != 0 && sub_08023C34(*p) == 3)
        r = 1;
    return r;
}
