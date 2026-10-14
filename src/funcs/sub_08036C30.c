#include "global.h"

extern u32 gUnk_020237E0[];

void sub_08036B0C(u8 *, u8 *, u32);
u32 sub_08038E30(u32, u32, u32, u32);

u32 sub_08036C30(u8 *a, u8 *b, u32 c)
{
    u8 i = 0;
    u32 r;

    while (i <= 2) {
        sub_08036B0C(a, b, c);
        r = sub_08038E30((u32)a, (u32)b, c, gUnk_020237E0[0]);
        if (r == 0) {
            break;
        }
        i++;
    }
    return r;
}
