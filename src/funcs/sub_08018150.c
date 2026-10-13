#include "global.h"

extern volatile u8 gUnk_02020B00[];
extern u8 gUnk_080BA25C[];

void sub_08006BE4(u16);

u8 sub_08018150(u16 a)
{
    sub_08006BE4(a);
    return gUnk_080BA25C[gUnk_02020B00[0x1D]];
}
