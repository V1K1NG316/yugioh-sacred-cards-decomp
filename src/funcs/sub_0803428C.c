#include "global.h"

void sub_0801827C(void);
void sub_080184E8(void);
void sub_080341B8(void);
void sub_08034304(void);
void sub_080343AC(u16);
void sub_08034450(u16);
u32  sub_08034478(u16);
void sub_08006BE4(u16);
void sub_08015DD8(void);
void sub_0801BED4(u16, u32);
void sub_08021E50(u16);

extern u8 gUnk_02023743[];
extern u8 gUnk_02023740[];
extern u8 gUnk_02020D90[];

void sub_0803428C(void)
{
    s32 i;

    sub_0801827C();

    for (i = 0; i <= 7; i++)
        gUnk_02023743[i] = gUnk_02020D90[i];

    sub_080341B8();

    if (gUnk_02023740[2] == 10) {
        sub_08006BE4(*(u16 *)gUnk_02023740);
        sub_08021E50(0x5F);
        sub_08015DD8();
        sub_0801BED4(*(u16 *)gUnk_02023740, 1);
    } else {
        sub_08034304();

        if (gUnk_02023740[2] == 10 && sub_08034478(*(u16 *)gUnk_02023740) == 0) {
            sub_08034450(*(u16 *)gUnk_02023740);
            sub_080343AC(*(u16 *)gUnk_02023740);
        }
    }

    sub_080184E8();
}
