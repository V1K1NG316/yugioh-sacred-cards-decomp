/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_020237D0[];
extern u8 gUnk_02020C38[];

u32  sub_08018D68(u16);
u32  sub_08035BEC(void);
void sub_08035AFC(void);
void sub_08028308(u32, u32);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802BDA0(void)
{
    u8 i;
    u8 *q = gUnk_020237D0;
    u32 *slots;

    q[2] = gUnk_02023480[2];
    q[3] = gUnk_02023480[3];
    slots = gUnk_02023270;
    *(u16 *)q = *(u16 *)slots[gUnk_02023480[2] * 5 + gUnk_02023480[3]];
    if (sub_08035BEC() != 1 || gUnk_02020C38[0] != 0) {
        u32 *list = slots;

        i = 0;
        list += 5;
        do {
            if (sub_08018D68(*(u16 *)list[i]) == 0)
                sub_08028308(list[i], 1);
            i++;
        } while (i <= 4);
        sub_08028308(gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
        if (gUnk_02020C38[0] == 0) {
            sub_08021E50(0x41);
            sub_08024F64(0x151);
            sub_08021E50(0x4B);
        }
    } else {
        sub_08035AFC();
    }
}
