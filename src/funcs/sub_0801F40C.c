#include "global.h"

void sub_0801F40C(void)
{
    *(volatile u16 *)0x04000208 = 0;
    *(volatile u16 *)0x04000200 &= 0xFF7F;
    *(volatile u16 *)0x04000208 = 1;
}
