#include "global.h"

extern u32 gUnk_02020C50[];

u32 sub_08014088(void);

u32 sub_08014610(void)
{
    if (sub_08014088() < gUnk_02020C50[0])
        return 0;
    return 1;
}
