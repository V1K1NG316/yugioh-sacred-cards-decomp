#include "global.h"

u32 sub_0801449C(void);

u32 sub_0800597C(void)
{
    u8 v = sub_0801449C();

    if (v <= 0x27)
        return 0x4000;
    return 0x5000;
}
