#include "global.h"

void sub_080284CC(void);
void sub_080284E4(void);

void sub_08005FE0(void)
{
    sub_080284CC();
    sub_080284E4();
    *(u16 *)0x04000000 = 0x7E00;
}
