/* compiler: agbcc (A37) */
#include "global.h"

void sub_080243A0(u16 *);
void sub_08028308(u16 *, u16);
void sub_08021E50(u16);
void sub_08024F64(u16);

extern u8 gUnk_02023298[];
extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

void sub_0802EB6C(void)
{
    u8 i = 0;
    u8 *list = gUnk_02023298;

    for (; i <= 4; i++) {
        u8 *c = *(u8 **)&list[i * 4];

        if (*(u16 *)c != 0 && *(s8 *)(c + 2) < 0)
            sub_080243A0((u16 *)c);
    }
    sub_08028308((u16 *)gUnk_02023270[(u8)gUnk_02023480[2] * 5 + (u8)gUnk_02023480[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x28F);
        sub_08021E50(0x49);
    }
}
