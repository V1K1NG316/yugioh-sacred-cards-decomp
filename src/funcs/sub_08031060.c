#include "global.h"

void sub_08021F10(u8);
void sub_08003BC4(void);


void sub_08031060(u8 n)
{
    u16 *reg = (u16 *)0x04000000;
    s32 j;

    reg[0] = 0x1C00;
    *(u16 *)0x04000050 = 0xFC;
    sub_08021F10(n);
    for (j = 0; j <= 0xF; j++) {
        s32 k;

        *(u16 *)0x04000054 = j;
        for (k = n - 1; k != -1; k--)
            sub_08003BC4();
    }
}
