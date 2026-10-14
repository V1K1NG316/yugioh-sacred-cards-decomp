#include "global.h"

void sub_08031AB8(void);
void sub_08030510(void);
void sub_08003BC4(void);
void sub_08030E14(void);

void sub_08031D58(void)
{
    sub_08031AB8();
    *(u16 *)0x04000000 = 0x4D00;
    sub_08030510();
    sub_08003BC4();
    sub_08030E14();
    *(u16 *)0x04000000 = 0x5D00;
}
