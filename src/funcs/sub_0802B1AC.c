#include "global.h"

extern u32 gUnk_02023284[];
extern u8 gUnk_02020C38[];

s32 sub_0802690C(u32);
u32 sub_08026B28(u32 *);
void sub_08028308(u32, u32);
u32 sub_0803691C(void);
void sub_080239E0(u16);
void sub_08023998(u16);
void sub_0802321C(void);
void sub_08023614(void);
void sub_08024F64(u16, u16);
void sub_08021E50(u16);

void sub_0802B1AC(void)
{
    if (sub_0802690C((u32)gUnk_02023284) <= 4)
        sub_08028308(gUnk_02023284[(u8)sub_08026B28(gUnk_02023284)], 1);
    if (sub_0803691C() == 0)
        sub_080239E0(500);
    else
        sub_08023998(500);
    sub_0802321C();
    sub_08023614();
    if (gUnk_02020C38[0] == 0) {
        sub_08024F64(0x367, 0x367);
        sub_08021E50(0x4C);
    }
}
