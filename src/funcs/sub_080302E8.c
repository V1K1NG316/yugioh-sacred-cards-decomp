#include "global.h"

void sub_0803032C(void);
void sub_080303B0(void);
void sub_080303FC(void);
void sub_08030510(void);
void sub_08003BC4(void);
void sub_08030DA0(void);


void sub_080302E8(void)
{
    u16 *d = (u16 *)0x04000000;

    d[0] = 0;
    *(u16 *)0x04000050 = 0;
    sub_0803032C();
    sub_080303B0();
    sub_080303FC();
    sub_08030510();
    *(u16 *)0x04000054 = 7;
    sub_08003BC4();
    sub_08030DA0();
    d[0] = 0x1D00;
}
