#include "global.h"

u32 sub_08023C34(u16);
u32 sub_08023C64(u16);

u32 sub_08026DDC(u16 *p)
{
    u32 r = 0;

    if (sub_08023C34(*p) == 2 && sub_08023C64(*p) == 0)
        r = 1;
    return r;
}
