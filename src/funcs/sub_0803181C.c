#include "global.h"

u32 sub_0803181C(u16 x)
{
    if (x & 0xFE00) {
        return 0;
    }
    if (x & 1) {
        return 1;
    }
    return 0;
}
