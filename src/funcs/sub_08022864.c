#include "global.h"

void sub_080284E4(void);

void sub_08022864(void)
{
    sub_080284E4();
    *(u16 *)0x04000000 = 0x1800;
}
