#include "global.h"

u32 sub_08031564(s32 a, s32 b)
{
    u32 f = 0;

    if (b <= 8) {
        f = (b >= 0);
    }
    if (a <= 4) {
        if (a >= -4) {
            f |= 2;
        }
    }
    if (f == 3) {
        return 1;
    }
    return 0;
}
