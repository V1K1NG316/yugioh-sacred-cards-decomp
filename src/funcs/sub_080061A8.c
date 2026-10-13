#include "global.h"

extern u32 gUnk_08D41B28[];

u32 sub_08036C30(u32, u32, u32);

u32 sub_080061A8(void)
{
    u32 a = 0x0E004020;
    return sub_08036C30(gUnk_08D41B28[0], a, 0x80A);
}
