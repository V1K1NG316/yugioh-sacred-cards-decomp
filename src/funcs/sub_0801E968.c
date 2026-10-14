#include "global.h"

void sub_080284CC(void);
void sub_080284A0(void);

void sub_0801E968(void)
{
    *(volatile u16 *)0x04000000 &= 0xFEFF;
    sub_080284CC();
    sub_080284A0();
}
