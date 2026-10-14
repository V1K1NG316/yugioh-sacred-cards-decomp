#include "global.h"

void sub_08036930(u32 a, u32 b);
void sub_0800917C(u8 *p, u8 a, u8 b);

void sub_08009118(u32 a, u32 b)
{
    sub_08036930(a, b);
    sub_0800917C((u8 *)b, 0xA, 0xA);
}
