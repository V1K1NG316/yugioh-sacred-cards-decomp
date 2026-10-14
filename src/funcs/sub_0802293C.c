#include "global.h"

void sub_080284A0(void);

void sub_0802293C(void)
{
    *(volatile u16 *)0x04000000 |= 0x2100;
    *(u16 *)0x02023464 = 0xA;
    sub_080284A0();
}
