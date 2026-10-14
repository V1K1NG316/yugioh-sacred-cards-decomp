#include "global.h"

void sub_080284CC(void);
void sub_080284A0(void);

void sub_0801EA90(void)
{
    *(u16 *)0x04000008 = 0x150C;
    *(volatile u16 *)0x04000000 |= 0x100;
    sub_080284CC();
    sub_080284A0();
}
