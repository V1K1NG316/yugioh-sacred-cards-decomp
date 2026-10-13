#include "global.h"

u32 sub_08019D24(void);
void sub_0800358C(u32, u32, u32);

void sub_08003718(void)
{
    u8 a = sub_08019D24();

    sub_0800358C(0x10, 8, a);
    sub_0800358C(0x14, 8, 6);
}
