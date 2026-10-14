#include "global.h"

void sub_080284E4(void);

void sub_08018CE8(void)
{
    sub_080284E4();
    *(volatile u16 *)0x04000000 = 0x1800;
}
