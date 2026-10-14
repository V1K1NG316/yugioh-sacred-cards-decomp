#include "global.h"

u32 sub_0803158C(s32 a, s32 b)
{
    u32 f = 0;

    if (a <= 8) {
        f = (a >= 0);
    }
    if (b <= 4) {
        if (b >= -4) {
            f |= 2;
        }
    }
    if (f == 3) {
        return 1;
    }
    return 0;
}
