#include "global.h"

extern u8 gUnk_08D2CA66[];

u16 sub_080178B0(u16);
void sub_08017A98(void *, u32, u16);

void sub_08017878(u32 a, u16 b, u16 c)
{
    u16 v = sub_080178B0(b);

    sub_08017A98(gUnk_08D2CA66 + v * 18, a, c);
}
