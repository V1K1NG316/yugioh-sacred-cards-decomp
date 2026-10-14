#include "global.h"

void sub_0803692C(const void *, void *, u32);

extern u32 gUnk_08D30D9C[];
extern u8 *gUnk_0201CB2C;

void sub_0800423C(u8 a, u8 *b)
{
    if ((u8)(a - 0x15) <= 2)
        sub_0803692C((const void *)gUnk_08D30D9C[a], gUnk_0201CB2C, 0x10);
    sub_0803692C((const void *)gUnk_08D30D9C[a], b, 0x10);
}
