#include "global.h"

s32 sub_080268FC(u32);
s32 sub_0802690C(u32);
s32 sub_08026A20(u32 *);
s32 sub_08026AC4(u32);
s32 sub_08026B28(u32 *);
s32 sub_080269A0(u32 *);
s32 sub_08026B98(u32 *);
void sub_080243BC(u16 *);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

extern u8 gUnk_02023284[];
extern u8 gUnk_02023478[];
extern u8 gUnk_02020C38[];

void sub_0802AF54(void)
{
    u32 base = (u32)gUnk_02023284;

    if (sub_080268FC(base) < 5) {
        u32 idx = sub_08026AC4(base);

        sub_080243BC((u16 *)*(u32 *)((u8)idx * 4 + base));
    }
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x346, 0x346);
        sub_08021E50(0x4A);
    }
}
