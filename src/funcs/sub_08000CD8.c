#include "global.h"

extern u32 gUnk_02018400[];

void sub_08000CD8(void)
{
    gUnk_02018400[0] = 0xC0002070;
    gUnk_02018400[1] = 0;
    gUnk_02018400[2] = 0xC0402070;
    gUnk_02018400[3] = 0x10;
}
