#include "global.h"

extern u8 gUnk_02020770[];

u32 sub_08008B74(u16 a)
{
    if (gUnk_02020770[a] == 0)
        return 0x4000;
    return 0x5000;
}
