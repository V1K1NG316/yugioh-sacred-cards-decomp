/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u32 gUnk_02023284[];
extern u8 gUnk_02020B00[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

void sub_08006BE4(u16);
u32  sub_08018D68(u16);
void sub_08028308(u32, u32);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802D54C(void)
{
    u8 i;
    u32 *list;
    u8 *db;

    i = 0;
    list = gUnk_02023284;
    db = gUnk_02020B00;
    do {
        sub_08006BE4(*(u16 *)list[i]);
        if (sub_08018D68(*(u16 *)(db + 0x10)) == 0) {
            if (db[0x16] == 1)
                sub_08028308(list[i], 1);
        }
        i++;
    } while (i <= 4);
    sub_08028308(gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x149);
        sub_08021E50(0x4C);
    }
}
