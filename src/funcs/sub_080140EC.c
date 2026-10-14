#include "global.h"

extern u8 gUnk_02020C40[];

u8 sub_0801411C(void);

void sub_080140EC(void)
{
    while (sub_0801411C() != 0)
        (*(u32 *)gUnk_02020C40)++;
}
