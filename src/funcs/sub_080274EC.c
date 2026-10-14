#include "global.h"

void sub_08021E50(u16);

extern u8 gUnk_02023438[];

void sub_080274EC(void)
{
    sub_08021E50(0x36);
    if (gUnk_02023438[1] == 0)
        gUnk_02023438[1] = gUnk_02023438[1] + 1;
    gUnk_02023438[1] = gUnk_02023438[1] - 1;
}
