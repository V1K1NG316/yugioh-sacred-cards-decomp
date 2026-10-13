#include "global.h"

extern u32 gUnk_08D34AB4[];

u32 sub_080271C4(u32);

void sub_0800AF3C(void)
{
    *(u32 *)(gUnk_08D34AB4[0] + 0x14F0) = sub_080271C4(2);
}
