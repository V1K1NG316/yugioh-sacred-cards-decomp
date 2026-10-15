/* compiler: agbcc (A37) */
#include "global.h"

extern u32 gUnk_02023270[];
extern u8 gUnk_02023480[];
extern u8 gUnk_02020C38[];

void sub_08028308(u32, u32);
void sub_08021E50(u16);
void sub_08024F64(u16);

void sub_0802D648(void)
{
    u8 i = 0;
    u32 *cur = gUnk_02023270;
    u8 *b = gUnk_02023480;
    u32 *list = cur;

    list += 5;
    do {
        if (*(u16 *)list[i] != 0)
            *(u8 *)(list[i] + 4) |= 0x10;
        i++;
    } while (i <= 4);
    sub_08028308(cur[b[2] * 5 + b[3]], 0);
    if (gUnk_02020C38[0] == 0) {
        sub_08021E50(0x41);
        sub_08024F64(0x15E);
        sub_08021E50(0x3C);
    }
}
