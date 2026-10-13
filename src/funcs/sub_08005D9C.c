#include "global.h"

void sub_080284CC(void);

void sub_08005D9C(void)
{
    sub_080284CC();
    ((u16 *)0x04000000)[0] = 0xBF00;
    ((u16 *)0x04000000)[0x29] = 6;
    ((u16 *)0x04000000)[0x2A] = 0xA;
    *(volatile u16 *)0x04000050 |= 8;
}
