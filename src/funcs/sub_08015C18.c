#include "global.h"

void sub_080284CC(void);
void sub_080284E4(void);
void sub_08015C5C(void);

void sub_08015C18(void)
{
    sub_080284CC();
    sub_080284E4();
    sub_08015C5C();
    *(volatile u16 *)0x04000000 |= 0x4000;
    *(volatile u16 *)0x04000000 &= 0xFEFF;
}
