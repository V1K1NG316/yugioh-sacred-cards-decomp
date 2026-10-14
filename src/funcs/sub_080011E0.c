#include "global.h"

void sub_080284A0(void);
void sub_08028438(void);

extern u16 gUnk_02018400[];
extern u16 gUnk_0202345C;
extern u16 gUnk_0202344C;
extern u16 gUnk_02023458;
extern u16 gUnk_02023474;
extern u16 gUnk_02023450;

void sub_080011E0(void)
{
    u16 i;

    for (i = 0; i <= 0x7F; i++) {
        gUnk_02018400[i * 4 + 0] = 0xA0;
        gUnk_02018400[i * 4 + 1] = 0xF0;
        gUnk_02018400[i * 4 + 2] = 0xC00;
        gUnk_02018400[i * 4 + 3] = 0;
    }

    *(u16 *)0x0400000E = 0x1383;
    *(u16 *)0x0400000C = 0x140E;
    *(u16 *)0x04000208 = 1;
    *(u16 *)0x04000200 = 1;
    *(u16 *)0x04000004 = 8;
    *(u16 *)0x04000000 = 0x1C00;
    gUnk_0202345C = 0;
    sub_080284A0();
    gUnk_0202344C = 0;
    gUnk_02023458 = 0;
    gUnk_02023474 = 0;
    gUnk_02023450 = 0xFF70;
    sub_08028438();
}
