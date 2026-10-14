#include "global.h"

void sub_080284E4(void);

void sub_08016210(void)
{
    sub_080284E4();
    *(volatile u16 *)0x04000000 = 0xE00;
}
