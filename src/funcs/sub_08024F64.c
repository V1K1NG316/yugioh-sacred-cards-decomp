#include "global.h"

extern u32 gUnk_08DFC054[];

void sub_08024F2C(u32, u16, u16, u16, u16);

void sub_08024F64(u16 a, u16 b)
{
    sub_08024F2C(gUnk_08DFC054[a], a, b, 0, 0);
}
