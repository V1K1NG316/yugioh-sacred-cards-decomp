#include "global.h"

extern u8 gUnk_0201EE58;
extern u8 gUnk_0201EE59;

void sub_0801950C(void)
{
    *(volatile u16 *)0x04000050 = 0x3FFF;
    gUnk_0201EE59 = 0x10;
    gUnk_0201EE58 = 0;
}
