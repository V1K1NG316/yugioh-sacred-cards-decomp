#include "global.h"

void sub_080016D8(void);

void sub_080016B0(void)
{
    *(u8 *)0x04000048 = 0x3C;
    *(u8 *)0x0400004A = 8;
    sub_080016D8();
}
