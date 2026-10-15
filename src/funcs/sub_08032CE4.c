#include "global.h"

void sub_08003BC4(void);

void sub_08032CE4(u8 frames)
{
    s32 i;

    *(volatile u16 *)0x04000000 = 0x1D00;
    *(volatile u16 *)0x04000050 = 0xDC;

    for (i = 0; i <= 0xF; i++) {
        u32 n;

        *(volatile u16 *)0x04000054 = i;

        n = frames;
        while (n-- != 0)
            sub_08003BC4();
    }
}
