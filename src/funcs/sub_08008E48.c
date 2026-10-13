#include "global.h"

void sub_080284CC(void);

void sub_08008E48(void)
{
    sub_080284CC();
    *(u16 *)0x04000000 = 0xBF00;
    *(u16 *)0x04000052 = 6;
    *(u16 *)0x04000054 = 0xA;
    *(volatile u16 *)0x04000050 |= 8;
}
