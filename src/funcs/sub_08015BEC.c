#include "global.h"

void sub_08015C5C(void);
void sub_080284CC(void);

void sub_08015BEC(void)
{
    sub_08015C5C();
    *(volatile u16 *)0x04000000 |= 0x4000;
    *(volatile u16 *)0x04000000 &= 0xFEFF;
    sub_080284CC();
}
