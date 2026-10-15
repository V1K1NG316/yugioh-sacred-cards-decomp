#include "global.h"

void sub_08006BE4(u16);
void sub_080243A8(u16 *);
void sub_080243BC(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02020B00[];
extern u8 gUnk_02023298[];
extern u8 gUnk_02020C38[];

void sub_08029868(void)
{
    u8 i = 0;
    u32 base = (u32)gUnk_02023298;

    for (; i < 5; i++) {
        u32 *e = (u32 *)(i * 4 + base);

        sub_08006BE4(*(u16 *)*e);

        if (gUnk_02020B00[0x17] == 1)
            sub_080243BC((u16 *)*e);

        if (gUnk_02020B00[0x17] == 2)
            sub_080243A8((u16 *)*e);
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x1EC, 0x1EC);
        sub_08021E50(0x49);
    }
}
