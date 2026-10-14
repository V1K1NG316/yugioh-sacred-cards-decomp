#include "global.h"

extern u8 *gUnk_02023298[];

u32 sub_08026CE4(void *, u16);
u32 sub_08026D0C(void *, u16);

u32 sub_08012324(u8 a, u16 *p)
{
    if (sub_08026CE4(gUnk_02023298, *p) == 1 && sub_08026D0C(gUnk_02023298, *p) == a)
        return 1;
    return 0;
}
