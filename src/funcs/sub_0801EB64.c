#include "global.h"

void sub_080284CC(void);
void sub_080284A0(void);

void sub_0801EB64(void)
{
    *(u16 *)0x04000008 = 0x140C;
    *(volatile u16 *)0x04000000 |= 0x100;
    sub_080284CC();
    sub_080284A0();
}
