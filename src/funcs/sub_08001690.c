#include "global.h"

extern u32 gUnk_02018400[];

void sub_08001690(u8 a)
{
    gUnk_02018400[0] = ((a << 4) + 0x38) | 0x40400000;
    gUnk_02018400[1] = 0x800;
}
