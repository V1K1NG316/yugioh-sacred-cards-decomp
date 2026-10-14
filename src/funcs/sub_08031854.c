#include "global.h"

u32 sub_08031854(u16 x)
{
    if (x & 0x200) {
        return 1;
    }
    if (x & 0x400) {
        return 2;
    }
    return 0;
}
