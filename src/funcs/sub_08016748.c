#include "global.h"

u32 sub_08016768(void);
void sub_0801BED4(u16, u16);

void sub_08016748(void)
{
    u32 i;

    for (i = 0; i < 0x32; i++)
        sub_0801BED4(sub_08016768(), 1);
}
