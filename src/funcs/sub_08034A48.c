#include "global.h"

extern u8 gUnk_08D51130[];

s32 sub_08034A48(u8 a, u8 b)
{
    u8 *p = gUnk_08D51130;

    return *(s16 *)(p + b * 2);
}
