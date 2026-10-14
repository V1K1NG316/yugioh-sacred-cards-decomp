#include "global.h"

extern u32 gUnk_08D4C16C[];

void sub_08024F2C(u32, u16, u16, u16, u16);

void sub_08024FC0(u8 a)
{
    sub_08024F2C(gUnk_08D4C16C[a - 1], 0, 0, 0, 0);
}
