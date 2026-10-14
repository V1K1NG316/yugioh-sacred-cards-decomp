#include "global.h"

void sub_080284CC(void);
void sub_080284E4(void);
void sub_08005EF0(void);

void sub_08005EAC(void)
{
    sub_080284CC();
    sub_080284E4();
    sub_08005EF0();
    *(volatile u16 *)0x04000000 |= 0x4000;
    *(volatile u16 *)0x04000000 &= 0xFEFF;
}
