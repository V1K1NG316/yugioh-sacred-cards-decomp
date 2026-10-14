#include "global.h"

void sub_080284E4(void);
void sub_080284CC(void);
void sub_08028514(void);

void sub_08007930(void)
{
    sub_080284E4();
    sub_080284CC();
    sub_08028514();
    ((u16 *)0x04000000)[0] = 0xBF00;
    ((u16 *)0x04000000)[0x29] = 6;
    ((u16 *)0x04000000)[0x2A] = 0xA;
    *(volatile u16 *)0x04000050 |= 8;
}
