#include "global.h"

extern u32 gUnk_08D356C0[];
extern u16 gUnk_02020C30;

u32 sub_08038E24(void *p);

u8 sub_0801174C(void)
{
    return sub_08038E24((void *)gUnk_08D356C0[gUnk_02020C30]);
}
