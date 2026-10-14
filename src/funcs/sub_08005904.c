#include "global.h"

u8 sub_08015810(u16);
u8 sub_0801449C(void);
void sub_08006BE4(u16);
u32 sub_08014110(void);

extern u8 gUnk_02020770[];
extern u32 gUnk_02020B00[];

u16 sub_08005904(u16 a)
{
    if (gUnk_02020770[a] == 0)
        return 0x4000;
    if (sub_08015810(a) != 1)
        return 0x4000;
    if (sub_0801449C() == 0x28)
        return 0x4000;
    sub_08006BE4(a);
    if (sub_08014110() < gUnk_02020B00[3])
        return 0x4000;
    return 0x5000;
}
