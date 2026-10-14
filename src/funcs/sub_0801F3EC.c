#include "global.h"

void sub_0801F3EC(void)
{
    *(volatile u16 *)0x04000208 = 0;
    *(volatile u16 *)0x04000200 |= 0x80;
    *(volatile u16 *)0x04000208 = 1;
}
