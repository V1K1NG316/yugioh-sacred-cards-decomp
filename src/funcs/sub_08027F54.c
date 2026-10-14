#include "global.h"

void sub_08021E50(u16);
void sub_08027694(void);
void sub_0802595C(void);
void sub_08025818(u8, u8);

extern u8 gUnk_02023438[];

void sub_08027F54(void)
{
    u8 v;

    sub_08021E50(0x38);
    v = gUnk_02023438[1];
    gUnk_02023438[4] = 0;
    sub_08027694();
    sub_0802595C();
    sub_08025818(v, gUnk_02023438[1]);
}
