#include "global.h"

u32 sub_08036C30(u32, u32, u32);

u32 sub_080063A0(void)
{
    u8 v = 3;

    return sub_08036C30((u32)&v, 0x0E000000, 1);
}
