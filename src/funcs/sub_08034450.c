#include "global.h"

extern u8 gUnk_020237C4[];

u32 sub_080231BC(u8);

void sub_08034450(u16 a)
{
    gUnk_020237C4[a >> 3] |= sub_080231BC(a & 7);
}
