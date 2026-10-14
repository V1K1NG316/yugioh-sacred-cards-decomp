#include "global.h"

u16 sub_0800475C(u32);
u8 sub_0801449C(void);
u8 sub_08015810(u16);
void sub_08006BE4(u16);
u32 sub_08014110(void);
void sub_080143C4(u16);
void sub_08021E50(u32);

extern u8 gUnk_02020770[];
extern u32 gUnk_02020B00[];

void sub_08004558(void)
{
    u16 id = sub_0800475C(2);
    u8 *p = &gUnk_02020770[id];

    if (*p != 0 && sub_0801449C() <= 0x27 && sub_08015810(id) == 1) {
        sub_08006BE4(id);
        if (sub_08014110() >= gUnk_02020B00[3])
            goto ok;
    }
    sub_08021E50(0x39);
    return;
ok:
    *p -= 1;
    sub_080143C4(id);
    sub_08021E50(0x37);
}
