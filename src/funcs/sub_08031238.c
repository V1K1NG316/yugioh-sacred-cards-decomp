#include "global.h"

u32 sub_08031238(u32 a, u8 b, u8 c)
{
    if (b == 0) {
        return 0;
    }
    if (b > 0x77) {
        return 0;
    }
    if (c == 0) {
        return 0;
    }
    if (c > 0x4F) {
        return 0;
    }
    return 1;
}
