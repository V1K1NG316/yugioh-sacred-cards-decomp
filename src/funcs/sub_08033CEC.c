#include "global.h"

u32 sub_08014110(void);

void sub_08033CEC(u8 *p)
{
    p[0x1e] = 0;
    if ((s32)sub_08014110() <= 0x4f)
        p[0x1e] = 1;
}
