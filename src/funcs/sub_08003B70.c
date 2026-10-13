#include "global.h"

extern u32 gUnk_0201CB24[];

void sub_080372D4(void);
void sub_080379A8(void);
void sub_08038E24(u32);
void sub_08003BAC(void);

void sub_08003B70(void)
{
    sub_080372D4();
    sub_080379A8();
    if (gUnk_0201CB24[0] != 0)
        sub_08038E24(gUnk_0201CB24[0]);
    sub_08003BAC();
}
