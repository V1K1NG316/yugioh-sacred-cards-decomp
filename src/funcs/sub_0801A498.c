#include "global.h"

void sub_0801A498(void)
{
    *(volatile u16 *)0x0400000A &= 0xE0FF;
    *(volatile u16 *)0x0400000A |= 0x1B00;
    *(volatile u16 *)0x0400000C &= 0xE0FF;
    *(volatile u16 *)0x0400000C |= 0x1E00;
    *(volatile u16 *)0x0400000E &= 0xE0FF;
    *(volatile u16 *)0x0400000E |= 0x1F00;
}
