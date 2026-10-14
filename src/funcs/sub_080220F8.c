#include "global.h"

void sub_080220F8(void)
{
    *(volatile u16 *)0x0201FCB0 &= 0xFF3F;
}
