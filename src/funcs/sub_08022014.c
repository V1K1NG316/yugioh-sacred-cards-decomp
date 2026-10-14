#include "global.h"

void sub_08022014(void)
{
    *(volatile u16 *)0x04000208 = 0;
    *(volatile u16 *)0x04000200 |= 0x40;
    *(volatile u16 *)0x04000208 = 1;
}
