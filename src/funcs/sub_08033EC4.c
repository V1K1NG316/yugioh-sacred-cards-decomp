#include "global.h"

u32 sub_08033DD8(u8 *, u16);

extern u8 gUnk_08175B1B[];

u8 sub_08033EC4(u16 a)
{
    return (u8)sub_08033DD8(gUnk_08175B1B, a);
}
