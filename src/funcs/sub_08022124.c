#include "global.h"

void sub_08022034(void);

void sub_08022124(void)
{
    sub_08022034();
    *(u16 *)0x0400010E = 0;
    *(u16 *)0x0400010C = 0xE4B1;
}
