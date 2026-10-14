#include "global.h"

u32 sub_08033DD8(u8 *, u16);

extern u8 gUnk_08175B8C[];

u8 sub_08033EE0(u16 a)
{
    return (u8)sub_08033DD8(gUnk_08175B8C, a);
}
