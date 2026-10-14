#include "global.h"

u32 sub_08019D24(void);

void sub_08033D08(u8 *p)
{
    u8 v;

    p[0x1e] = 0;
    v = sub_08019D24();
    if (v == 6)
        p[0x1e] = 1;
}
