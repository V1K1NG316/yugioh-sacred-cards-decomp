#include "global.h"

extern u8 gUnk_08D2AAEA[];

u16 sub_080178B0(u16);
void sub_0801798C(void *, u32, u16);

void sub_08017808(u32 a, u16 b, u16 c)
{
    u16 v = sub_080178B0(b);

    sub_0801798C(gUnk_08D2AAEA + v * 10, a, c);
}
