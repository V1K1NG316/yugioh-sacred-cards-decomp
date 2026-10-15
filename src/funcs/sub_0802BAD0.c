/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_020237D0[];
extern u8 gUnk_02020C38[];

void sub_08028308(u32, u32);
u32  sub_08035BEC(void);
void sub_08035AFC(u16);
u32  sub_0803691C(void);
void sub_080239E0(u16);
void sub_08023998(u16);
void sub_0802321C(void);
void sub_08023614(void);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802BAD0(void)
{
    u8 *q = gUnk_020237D0;

    q[2] = gUnk_02023480[2];
    q[3] = gUnk_02023480[3];
    *(u16 *)q = *(u16 *)gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]];
    if (sub_08035BEC() != 1 || gUnk_02020C38[0] != 0) {
        if (sub_0803691C() == 0)
            sub_080239E0(200);
        else
            sub_08023998(200);
        sub_0802321C();
        sub_08023614();
        sub_08028308(gUnk_02023270[gUnk_02023480[2] * 5 + gUnk_02023480[3]], 0);
        if (gUnk_02020C38[0] == 0) {
            sub_08021E50(0x41);
            sub_08024F64(0x159);
            sub_08021E50(0x4D);
        }
    } else {
        sub_08035AFC(200);
    }
}
