#include "global.h"

extern u16 gUnk_02018400[];

void sub_0801C6D0(void)
{
    gUnk_02018400[0x14] = 0xA0;
    gUnk_02018400[0x15] = 0xF0;
    gUnk_02018400[0x16] = 0xC0 << 4;
    gUnk_02018400[0x17] = 0;
}
