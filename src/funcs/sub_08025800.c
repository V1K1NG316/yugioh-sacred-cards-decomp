#include "global.h"

extern u16 gUnk_02023450[];
extern u8 gUnk_08D4C2C1[];

void sub_08025800(u8 a)
{
    gUnk_02023450[0] = gUnk_08D4C2C1[a];
}
