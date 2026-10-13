#include "global.h"

extern u32 gUnk_08D41B28[];
extern u32 gUnk_020237DC[];

void sub_08038E30(u32, u32, u32, u32);
void sub_08021FB8(void);

void sub_080061F4(void)
{
    u32 t = gUnk_08D41B28[0];
    u32 a = 0x0E004020;
    u32 *p = &gUnk_020237DC[0];

    sub_08038E30(a, t, 0x80A, *p);
    sub_08021FB8();
}
