#include "global.h"

void sub_080369C0(u8 *, u8 *, u32);
u32 sub_08036A30(u8 *, u8 *, u32);

u32 sub_08036A94(u8 *a, u8 *b, u32 c)
{
    u8 i = 0;
    u32 r;

    while (i <= 2) {
        sub_080369C0(a, b, c);
        r = sub_08036A30(a, b, c);
        if (r == 0) {
            break;
        }
        i++;
    }
    return r;
}
