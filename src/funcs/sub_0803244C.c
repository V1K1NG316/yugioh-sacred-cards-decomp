#include "global.h"

void sub_0803244C(u8 *p)
{
    if (p[0xD] == 1) {
        *(u32 *)(p + 8) = 0;
    } else {
        *(u32 *)(p + 8) = 1;
    }
}
