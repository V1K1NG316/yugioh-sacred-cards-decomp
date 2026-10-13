#include "global.h"

extern u32 gUnk_0201CB28[];
extern u32 gUnk_08D30E8C[];

void sub_0803692C(u32, u32, u32);

void sub_08004284(u8 a, u32 b)
{
    gUnk_0201CB28[0] = b;
    sub_0803692C(gUnk_08D30E8C[a], b, 0x40);
}
