#include "global.h"

extern u32 gUnk_0201CB24[];

void sub_08003B94(void);

void sub_08003B58(void *p)
{
    gUnk_0201CB24[0] = (u32)p;
    if (p == 0)
        gUnk_0201CB24[0] = 0x08003B95;
}
