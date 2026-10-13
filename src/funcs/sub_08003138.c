#include "global.h"

extern u16 gUnk_02000400[];

void sub_08003138(u8 a, u8 b, u16 c, u16 v)
{
    gUnk_02000400[(c >> 1) + b * 32 + a] = v;
}
