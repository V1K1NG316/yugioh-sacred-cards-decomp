#include "global.h"

void sub_080284E4(void);

void sub_080128F8(void)
{
    sub_080284E4();
    *(u16 *)0x0400000C = 0x1E81;
    *(u16 *)0x0400000E = 0x1F86;
    *(u16 *)0x04000000 = 0xC00;
}
