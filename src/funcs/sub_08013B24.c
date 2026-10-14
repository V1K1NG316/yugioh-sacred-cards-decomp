#include "global.h"

void sub_080284CC(void);
void sub_080284E4(void);
void sub_080284A0(void);

void sub_08013B24(void)
{
    sub_080284CC();
    sub_080284E4();
    sub_080284A0();
    *(volatile u16 *)0x04000000 |= 0x1000;
}
