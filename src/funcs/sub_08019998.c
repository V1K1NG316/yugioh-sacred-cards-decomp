#include "global.h"

void sub_080284E4(void);
void sub_08028438(void);

extern u16 gUnk_02023458[];
extern u16 gUnk_0202344C[];

void sub_08019998(void)
{
    sub_080284E4();
    gUnk_02023458[0] = 0;
    gUnk_0202344C[0] = 0;
    sub_08028438();
    *(volatile u16 *)0x0400000E = (*(volatile u16 *)0x0400000E & 0xE0F3);
    *(volatile u16 *)0x0400000E |= 0x1C00;
    *(volatile u16 *)0x0400000E |= 0xC;
    *(volatile u16 *)0x04000000 = 0x800;
}
