#include "global.h"

void sub_0801A4F8(void)
{
    *(volatile u16 *)0x0400000A &= 0xE0FF;
    *(volatile u16 *)0x0400000A |= 0x1A00;
    *(volatile u16 *)0x0400000C &= 0xE0FF;
    *(volatile u16 *)0x0400000C |= 0x1C00;
    *(volatile u16 *)0x0400000E &= 0xE0FF;
    *(volatile u16 *)0x0400000E |= 0x1D00;
}
