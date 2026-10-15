#include "global.h"

extern u16 gUnk_0202347C[];
extern u8 gUnk_02020D30[];

void sub_0802B2D8(void)
{
    u16 *dst = gUnk_0202347C;
    u8 *p = gUnk_02020D30;

    dst[0] = *(u16 *)(p + 0x40);
    dst[1] = *(u16 *)(p + 0x42);
}
