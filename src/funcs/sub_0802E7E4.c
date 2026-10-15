/* compiler: agbcc (A37) */
#include "global.h"

u32 sub_08026CE4(u32 *, u16);
u32 sub_08026D0C(u32 *, u16);
void sub_0802FCC8(u16 *, u16);
void sub_08028308(u16 *, u16);
void sub_08028378(void);
void sub_08021E50(u16);
void sub_08024F64(u16, u16);

extern u8 gUnk_02023298[];
extern u8 gUnk_08D36328[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

void sub_0802E7E4(void)
{
    u8 *list = gUnk_02023298;
    u8 *cards = gUnk_08D36328;
    u8 idx;
    u32 *q;

    if (sub_08026CE4((u32 *)list, *(u16 *)(cards + 0xb0)) != 1)
        return;
    idx = (u8)sub_08026D0C((u32 *)list, *(u16 *)(cards + 0xb0));
    q = (u32 *)(list - 0x28);
    sub_08028308((u16 *)q[(u8)gUnk_02023480[2] * 5 + (u8)gUnk_02023480[3]], 0);
    sub_0802FCC8((u16 *)((u32 *)list)[idx], *(u16 *)(cards + 0xb2));
    sub_08028378();
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x2bb, *(u16 *)(cards + 0xb2));
        sub_08021E50(0x53);
    }
}
