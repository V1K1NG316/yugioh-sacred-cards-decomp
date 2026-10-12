#include "global.h"

extern u16 gUnk_02000400[];

u16 sub_08003118(u8 x, u8 y, u16 z)
{
    return gUnk_02000400[(z >> 1) + y * 32 + x];
}
