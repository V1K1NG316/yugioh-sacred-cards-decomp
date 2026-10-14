#include "global.h"

extern u8 gUnk_02000400[];

void sub_0802280C(void)
{
    u8 *p = gUnk_02000400;

    *(u16 *)(p + 0xF2DA) = 0;
    *(u16 *)(p + 0xF31A) = 1;
}
