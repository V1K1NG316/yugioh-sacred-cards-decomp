#include "global.h"

void sub_08028308(u16 *, u8);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);
u32 sub_08018D68(u16);

extern u8 gUnk_02023284[];
extern u8 gUnk_02020C38[];

void sub_0802AA74(void)
{

    u8 i = 0;
    u32 *tab = (u32 *)gUnk_02023284;

    for (; i < 5; i++) {
        u32 *e = (u32 *)(i * 4 + (u32)tab);

        if (sub_08018D68(*(u16 *)*e) == 0)
            sub_08028308((u16 *)*e, 1);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x369, 0x369);
        sub_08021E50(0x4B);
    }
}
