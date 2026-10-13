#include "global.h"

u32 sub_08036A94(u32, u32, u32);

u32 sub_08006368(void)
{
    u8 v = 1;

    return sub_08036A94((u32)&v, 0x0E000000, 1);
}
