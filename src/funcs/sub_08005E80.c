#include "global.h"

void sub_080284CC(void);
void sub_08005EF0(void);

void sub_08005E80(void)
{
    sub_080284CC();
    sub_08005EF0();
    *(volatile u16 *)0x04000000 |= 0x4000;
    *(volatile u16 *)0x04000000 &= 0xFEFF;
}
