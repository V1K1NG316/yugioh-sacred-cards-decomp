#include "global.h"

extern u32 gUnk_0201CB2C[];
extern u32 gUnk_08D30E5C[];

void sub_0803692C(u32, u32, u32);

void sub_080042A8(u8 a, u32 b)
{
    gUnk_0201CB2C[0] = b;
    sub_0803692C(gUnk_08D30E5C[a], b, 0x10);
}
