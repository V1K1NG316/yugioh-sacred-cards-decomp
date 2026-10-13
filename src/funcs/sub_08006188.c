#include "global.h"

extern u32 gUnk_08D41B28[];

u32 sub_08036C30(u32, u32, u32);

u32 sub_08006188(void)
{
    u32 a = 0x0E000040;
    return sub_08036C30(gUnk_08D41B28[0], a, 0x80A);
}
