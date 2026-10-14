#include "global.h"

void sub_080284E4(void);

void sub_0801A470(void)
{
    sub_080284E4();
    *(u16 *)0x04000000 = 0x1E00;
}
