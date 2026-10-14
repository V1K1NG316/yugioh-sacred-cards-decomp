#include "global.h"

u32 sub_08023C34(u16);

void sub_0802832C(u16 *p, u16 v)
{
    if (sub_08023C34(v) == 1)
        *p = v;
}
