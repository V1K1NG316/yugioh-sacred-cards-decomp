#include "global.h"

void sub_080284CC(void);
void sub_080284E4(void);

void sub_0801371C(void)
{
    sub_080284CC();
    sub_080284E4();
    *(volatile u16 *)0x04000000 |= 0x1000;
}
