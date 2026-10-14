#include "global.h"

extern u8 gUnk_02023120[];
extern u16 gUnk_0202347C[];

void sub_08023998(u16 a)
{
    u16 *p = (u16 *)gUnk_02023120;
    u8 *q = (u8 *)p;
    u8 z = 0;

    q[0x18] = 8;
    q[0x1A] = z;
    q[0x1B] = 1;
    p[1] = a;
    p[3] = gUnk_0202347C[0];
    p[9] = gUnk_0202347C[1];
}
