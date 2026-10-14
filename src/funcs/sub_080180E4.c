#include "global.h"

void sub_080284CC(void);

void sub_080180E4(void)
{
    sub_080284CC();
    ((u16 *)0x04000000)[0x26] = 0;
    ((volatile u16 *)0x04000000)[4] |= 0x40;
    ((volatile u16 *)0x04000000)[5] |= 0x40;
    ((volatile u16 *)0x04000000)[6] |= 0x40;
    ((volatile u16 *)0x04000000)[7] |= 0x40;
}
