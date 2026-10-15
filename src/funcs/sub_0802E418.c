/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u32 gUnk_02023298[];
extern u16 gUnk_08D36328[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

u32  sub_08026CE4(u32, u16);
u32  sub_08026D0C(u32, u16);
void sub_08028308(u32, u32);
void sub_0802FCC8(u32, u16);
void sub_08028378(void);
void sub_08021E50(u16);
void sub_08024F64(u16, u16);

void sub_0802E418(void)
{
    u32 *list = gUnk_02023298;
    u16 *tbl = gUnk_08D36328;

    if (sub_08026CE4((u32)list, tbl[0x3C]) == 1) {
        u32 i = (u8)sub_08026D0C((u32)list, tbl[0x3C]);
        u32 *slots = list;

        slots -= 10;
        sub_08028308(slots[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
        sub_0802FCC8(list[i], tbl[0x3D]);
        sub_08028378();
        if (gUnk_02020C38[0] == 0) {
            sub_08021E50(0x41);
            sub_08024F64(0x2B4, tbl[0x3D]);
            sub_08021E50(0x53);
        }
    }
}
