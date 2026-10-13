#include "global.h"

u32 sub_08014570(void);
u32 sub_08014088(void);

u32 sub_0800595C(void)
{
    u32 a = sub_08014570();
    u32 b = sub_08014088();

    if (a > b)
        return 0x4000;
    return 0x5000;
}
